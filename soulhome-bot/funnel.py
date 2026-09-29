"""Автоворонка «Офис к Новому году» для компаний.

Вход: t.me/SoulHomeRuBot?start=office (или ?start=checklist) — с лид-магнита на сайте, из звонка, рассылки.
Дальше бот сам присылает серию сообщений по расписанию (только по будням 10:00–19:00 МСК)
и останавливается, как только клиент оставил заявку: прислал фото, номер телефона
или нажал «Рассчитать смету» / «Подобрать палитру» / «Закрепить дату» / «Обсудить сейчас».
Мастер получает карточку заявки и отвечает клиенту reply-ем, как и на остальные заявки.

Тексты — в STEPS ниже; их можно менять, не трогая остальной код.
Состояние хранится в funnel.json рядом с ботом, поэтому перезапуск бота воронку не сбрасывает.
Статистика для мастера — команда /funnel в его чате.
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

log = logging.getLogger("soulhome.funnel")
MSK = ZoneInfo("Europe/Moscow")
STATE_FILE = Path(__file__).parent / "funnel.json"
WORK_FROM, WORK_TO = 10, 19          # окно отправки, часы по Москве
WORKDAYS = {0, 1, 2, 3, 4}           # пн–пт
CHECK_EVERY = 60                     # как часто проверять очередь, секунд
ENTRY_ARGS = {"office", "checklist"}  # глубокие ссылки, которые запускают воронку

# ---------- тексты ----------
PACKAGES = (
    "📄 Пакеты оформления «под ключ»\n\n"
    "Базовый — концепция, ёлка с гирляндой, входная зона или ресепшн, монтаж, демонтаж и вывоз.\n\n"
    "Оптимальный — 80 000 ₽. Всё из «Базового» + фотозона и авторские бархатные шары ручной работы. Выбирают чаще всего.\n\n"
    "Расширенный — всё из «Оптимального» + оформление столов и зала корпоратива и шары с логотипом в подарок сотрудникам.\n\n"
    "Точная стоимость зависит от площади, высоты ёлки и числа зон — её пришлём после фото помещения или 30-минутного выезда дизайнера."
)

CHECKLIST = (
    "Мур, {name}! Вот чек-лист «Офис к новогоднему корпоративу за 7 шагов» 🎄\n\n"
    "1. За 8 недель — бюджет и кто утверждает концепцию. Средний проект под ключ — около 80 000 ₽.\n"
    "2. За 7 недель — палитра под фирменный стиль по правилу 60 · 30 · 10.\n"
    "3. За 6 недель — список зон: вход, ёлка, фотозона, столы. Замерьте высоту потолков.\n"
    "4. За 5 недель — дата монтажа. Вторая половина декабря расписывается первой.\n"
    "5. За 4 недели — концепция и смета. Проверьте, что в неё входят монтаж, демонтаж и вывоз.\n"
    "6. За 1–2 дня — монтаж вечером или в выходной. Тёплый свет 2700–3000 K.\n"
    "7. После праздников — демонтаж и хранение. Шары с логотипом можно подарить сотрудникам.\n\n"
    "🎁 Хотите бесплатную концепцию оформления вашего офиса? Пришлите сюда 3–4 фото помещения — "
    "дизайнер подготовит палитру под ваш бренд и план зон за 2 рабочих дня."
)

HOW_PHOTO = ("📷 Просто отправьте фото сюда, в чат — одним или несколькими сообщениями: вход, место под ёлку и зону, "
             "где будет праздник. В подписи можно указать дату корпоратива и что оформить.")

# кнопки: (текст, действие). Действия: photo, phone, packages, lead:<тема>, remind, stop
BTN_START = [("📷 Как прислать фото", "photo"), ("📞 Оставить телефон", "phone"), ("📄 Пакеты и цены", "packages")]

# шаги прогрева: через сколько часов после входа, текст, кнопки
STEPS = [
    {"after_h": 2, "text": (
        "Кстати, концепция — бесплатно и ни к чему не обязывает 🐾\n\n"
        "Достаточно 3–4 фото: вход, место под ёлку и зона, где будет праздник. "
        "Через 2 рабочих дня пришлём палитру под ваш фирменный стиль и план зон."),
     "buttons": [("📷 Как прислать фото", "photo")]},
    {"after_h": 24, "text": (
        "Урок дня: почему одни офисы на фото выглядят дорого, а другие — пёстро.\n\n"
        "Секрет — правило 60 · 30 · 10:\n"
        "— 60% основной цвет: хвоя, крупные шары, текстиль;\n"
        "— 30% поддерживающий: ленты, средние шары, свечи;\n"
        "— 10% акцент: золото или фирменный цвет компании.\n\n"
        "Не больше трёх цветов — и пространство выглядит собранным. Подобрать палитру под ваш бренд?"),
     "buttons": [("🎨 Подобрать палитру под наш бренд", "lead:palette")]},
    {"after_h": 72, "text": (
        "4 ошибки, из-за которых новогодний офис выглядит «как у всех»:\n\n"
        "1. Сотрудники наряжают сами, после работы — выходит наспех.\n"
        "2. Декор из разных магазинов — цвета спорят, ёлка плоская.\n"
        "3. Нет фотозоны — на снимках с праздника не видно стиля компании.\n"
        "4. Никто не подумал про демонтаж — коробки стоят до весны.\n\n"
        "Мы берём всё на себя: концепция, монтаж за одну смену вечером или в выходной, демонтаж и вывоз."),
     "buttons": [("📄 Пакеты и цены", "packages")]},
    {"after_h": 120, "text": PACKAGES,
     "buttons": [("✍️ Рассчитать смету", "lead:estimate")]},
    {"after_h": 168, "text": (
        "Про даты 📅\n\n"
        "Монтаж мы делаем за одну смену, но смен в декабре ограниченное число, и вторая половина месяца уходит первой. "
        "Давайте закрепим за вами дату сейчас — концепцию можно доработать позже."),
     "buttons": [("📌 Закрепить дату", "lead:date")]},
    {"after_h": 288, "text": (
        "Это последнее сообщение из серии 🐾\n\n"
        "Если с оформлением в этом году уже всё решено — напомнить о нас в следующем сезоне?"),
     "buttons": [("🔔 Напомнить в октябре", "remind"), ("✍️ Обсудить сейчас", "lead:talk"), ("🚫 Больше не писать", "stop")]},
]

REMIND_TEXT = ("Мур! Новогодний сезон начинается 🎄 Самое время подумать об оформлении офиса к корпоративу — "
               "лучшие даты монтажа в декабре разбирают первыми. Напомню, как всё устроено:")

LEAD_TITLES = {
    "photo": "фото помещения", "phone": "номер телефона", "estimate": "хочет рассчитать смету",
    "palette": "хочет палитру под бренд", "date": "хочет закрепить дату монтажа", "talk": "хочет обсудить сейчас",
}
BTN_SHARE = "📱 Отправить мой номер"
BTN_CANCEL = "Отмена"

# ---------- состояние ----------
_state: dict[str, dict] = {}


def _load() -> None:
    global _state
    try:
        _state = json.loads(STATE_FILE.read_text())
    except Exception:
        _state = {}


def _save() -> None:
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_state, ensure_ascii=False))
        tmp.replace(STATE_FILE)
    except Exception as e:
        log.warning("Не удалось сохранить funnel.json: %s", e)


def is_active(chat_id: int) -> bool:
    s = _state.get(str(chat_id))
    return bool(s and s.get("status") == "active")


def in_window(ts: float) -> float:
    """Сдвигает момент отправки в ближайшее рабочее окно (будни 10–19 по Москве)."""
    dt = datetime.fromtimestamp(ts, MSK)
    for _ in range(8):
        if dt.weekday() in WORKDAYS and WORK_FROM <= dt.hour < WORK_TO:
            return dt.timestamp()
        if dt.weekday() in WORKDAYS and dt.hour < WORK_FROM:
            dt = dt.replace(hour=WORK_FROM, minute=0, second=0, microsecond=0)
        else:
            dt = (dt + timedelta(days=1)).replace(hour=WORK_FROM, minute=0, second=0, microsecond=0)
    return dt.timestamp()


def _schedule(s: dict) -> None:
    step = s["step"]
    if step >= len(STEPS):
        s["status"], s["next_at"] = "finished", None
        return
    s["next_at"] = in_window(s["started"] + STEPS[step]["after_h"] * 3600)


def kb(buttons) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, callback_data=f"fn:{a}")] for t, a in buttons])


# ---------- вход в воронку ----------
async def enter(update: Update, context: ContextTypes.DEFAULT_TYPE, source: str = "office") -> None:
    chat = update.effective_chat.id
    u = update.effective_user
    s = _state.get(str(chat), {})
    s.update({"name": u.first_name or "", "username": u.username or "", "source": source,
              "started": time.time(), "step": 0, "status": "active", "entered": s.get("entered", 0) + 1})
    _schedule(s)
    _state[str(chat)] = s
    _save()
    await update.effective_message.reply_text(CHECKLIST.format(name=u.first_name or "друг"), reply_markup=kb(BTN_START))


# ---------- заявка ----------
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str, notify_admin, extra: str = "") -> bool:
    """Останавливает воронку и отправляет мастеру карточку заявки."""
    chat = str(update.effective_chat.id)
    s = _state.setdefault(chat, {"started": time.time(), "step": 0})
    s.update({"status": "lead", "next_at": None, "lead_topic": topic, "lead_at": time.time()})
    _save()
    body = f"Воронка «Офис к Новому году», шаг {s.get('step', 0)} из {len(STEPS)}.\nКлиент: {LEAD_TITLES.get(topic, topic)}."
    if extra:
        body += f"\n{extra}"
    return await notify_admin(context, update, "🏢 Заявка: оформление офиса", body)


def make_handlers(notify_admin, menu):
    async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        q = update.callback_query
        await q.answer()
        action = (q.data or "").removeprefix("fn:")
        msg = q.message
        if action == "photo":
            await msg.reply_text(HOW_PHOTO)
        elif action == "phone":
            await msg.reply_text("Нажмите кнопку ниже — номер придёт мастеру, и он перезвонит в рабочее время.",
                                 reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_SHARE, request_contact=True)], [BTN_CANCEL]],
                                                                  resize_keyboard=True, one_time_keyboard=True))
        elif action == "packages":
            await msg.reply_text(PACKAGES, reply_markup=kb([("✍️ Рассчитать смету", "lead:estimate")]))
        elif action.startswith("lead:"):
            sent = await convert(update, context, action[5:], notify_admin)
            await msg.reply_text(
                ("Готово! Передал мастеру — он напишет вам здесь в рабочее время. " if sent else
                 "Записал! Мастер скоро свяжется с вами. ") +
                "Чтобы ускорить расчёт, пришлите 3–4 фото помещения 🐾", reply_markup=menu)
        elif action == "remind":
            s = _state.setdefault(str(update.effective_chat.id), {})
            now = datetime.now(MSK)
            year = now.year + (1 if now.month >= 9 else 0)  # сезон уже идёт — напоминаем в следующем
            s.update({"status": "remind", "next_at": datetime(year, 10, 1, 11, 0, tzinfo=MSK).timestamp()})
            _save()
            await msg.reply_text("Договорились! Напишу 1 октября 🔔 Если понадобится раньше — просто напишите сюда.")
        elif action == "stop":
            await stop_cmd(update, context)

    async def on_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        c = update.message.contact
        phone = c.phone_number if c else ""
        sent = await convert(update, context, "phone", notify_admin, extra=f"Телефон: {phone}")
        await update.message.reply_text(
            "Спасибо! Номер у мастера — он позвонит в рабочее время. " if sent else "Спасибо, номер записал! ",
            reply_markup=menu)

    async def on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Хорошо 🐾 Можно просто прислать фото помещения или написать вопрос.", reply_markup=menu)

    async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        s = _state.setdefault(str(update.effective_chat.id), {})
        s.update({"status": "stopped", "next_at": None})
        _save()
        await update.effective_message.reply_text("Хорошо, больше не буду писать первым. Если понадоблюсь — я здесь 🐾", reply_markup=menu)

    return on_button, on_contact, on_cancel, stop_cmd


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, admin_id: int) -> None:
    if update.effective_chat.id != admin_id:
        return
    rows = list(_state.values())
    by = lambda st: sum(1 for r in rows if r.get("status") == st)
    steps = [sum(1 for r in rows if r.get("step", 0) > i) for i in range(len(STEPS))]
    topics = {}
    for r in rows:
        if r.get("status") == "lead":
            t = LEAD_TITLES.get(r.get("lead_topic"), r.get("lead_topic"))
            topics[t] = topics.get(t, 0) + 1
    total = len(rows)
    leads = by("lead")
    text = (f"📊 Воронка «Офис к Новому году»\n\nВошли: {total}\nЗаявки: {leads}"
            + (f" ({leads * 100 // total}%)" if total else "") +
            f"\nВ прогреве сейчас: {by('active')}\nОтписались: {by('stopped')}\nНапомнить в сезоне: {by('remind')}\n"
            f"Дошли до конца без заявки: {by('finished')}\n\nПолучили сообщение прогрева:\n" +
            "\n".join(f"{i + 1}) через {STEPS[i]['after_h']} ч — {n}" for i, n in enumerate(steps)) +
            ("\n\nЗаявки по типу:\n" + "\n".join(f"— {k}: {v}" for k, v in topics.items()) if topics else ""))
    await update.message.reply_text(text)


# ---------- рассылка по расписанию ----------
async def _tick(app: Application) -> None:
    now = time.time()
    due = [(cid, s) for cid, s in _state.items()
           if s.get("status") in ("active", "remind") and s.get("next_at") and s["next_at"] <= now]
    for cid, s in due:
        try:
            if s["status"] == "remind":
                await app.bot.send_message(int(cid), REMIND_TEXT)
                await app.bot.send_message(int(cid), CHECKLIST.format(name=s.get("name") or "друг"), reply_markup=kb(BTN_START))
                s.update({"status": "active", "started": now, "step": 0})
            else:
                step = STEPS[s["step"]]
                await app.bot.send_message(int(cid), step["text"], reply_markup=kb(step["buttons"]))
                s["step"] += 1
            _schedule(s)
        except Exception as e:  # бот заблокирован, чат удалён и т. п.
            log.warning("Воронка: не удалось написать %s: %s", cid, e)
            s.update({"status": "blocked", "next_at": None})
        _save()
        await asyncio.sleep(0.1)  # не упираемся в лимиты Telegram


async def _loop(app: Application) -> None:
    while True:
        try:
            await _tick(app)
        except Exception as e:
            log.exception("Воронка: ошибка очереди: %s", e)
        await asyncio.sleep(CHECK_EVERY)


def start_loop(app: Application) -> None:
    app.create_task(_loop(app))
    log.info("Воронка «Офис к Новому году»: %d контактов в базе", len(_state))


def register(app: Application, notify_admin, menu, admin_id: int) -> None:
    """Подключает воронку к боту. Вызывать ДО общих обработчиков сообщений."""
    _load()
    on_button, on_contact, on_cancel, stop_cmd = make_handlers(notify_admin, menu)
    app.add_handler(CallbackQueryHandler(on_button, pattern=r"^fn:"))
    app.add_handler(MessageHandler(filters.CONTACT, on_contact))
    app.add_handler(MessageHandler(filters.Text([BTN_CANCEL]), on_cancel))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("funnel", lambda u, c: stats_cmd(u, c, admin_id)))
