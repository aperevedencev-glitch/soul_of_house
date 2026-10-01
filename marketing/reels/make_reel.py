"""Рилс Soul of Home: 8 бесплатных уроков. 1080×1920, 30 fps, H.264 + тихая дорожка AAC.
Сцены: заставка → 8 уроков (проезд камеры по инфографике) → финал. Переходы — мягкое растворение."""
import math, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, '..', '..', 'docs', 'img') + os.sep   # картинки уроков с сайта
PINE, PINE2, IVORY, GOLD, GOLD_SOFT = (14, 28, 22), (22, 40, 31), (246, 241, 228), (199, 154, 70), (228, 199, 126)

LESSONS = [
    ('Цвет', 'Палитра ёлки и комнаты по правилу 60 · 30 · 10', 'Три цвета в нужной пропорции дают спокойную и собранную картинку вместо пёстрой.', 'palette-room.jpg'),
    ('Свет', 'Тёплый свет: 2700 K и три уровня освещения', 'Главная причина «неуютной» комнаты — одна холодная люстра под потолком.', 'lesson-light.jpg'),
    ('Фактура', 'Правило трёх текстур', 'Гладкое, мягкое и рельефное рядом — и однотонный интерьер становится тёплым.', 'lesson-textures.jpg'),
    ('Ручная работа', 'Как сделать первый бархатный шар', 'Мастер-класс в 6 шагов: бархат, вышивка, бусины, шапочка и лента.', 'masterclass-velvet.jpg'),
    ('Праздник', 'Как нарядить ёлку, чтобы она выглядела объёмной', 'Порядок украшения, от которого зависит, будет ли ёлка «дизайнерской».', 'masterclass-tree.jpg'),
    ('Текстиль', 'Подушки и пледы: как сочетать текстиль', 'Самый быстрый способ сменить настроение комнаты к сезону — без ремонта.', 'lesson-pillows.jpg'),
    ('Уход', 'Как хранить бархатные и вышитые игрушки', 'Чтобы шары ручной работы оставались красивыми через десять лет.', 'lesson-storage.jpg'),
    ('Подарки', 'Как упаковать подарок ручной работы', 'Упаковка и открытка с историей делают из вещи подарок, который сохраняют.', 'lesson-gift.jpg'),
]
T_INTRO, T_LESSON, T_OUTRO, T_X = 2.8, 4.6, 3.6, 0.45   # секунды; T_X — растворение между сценами

# ---------- шрифты ----------
LORA = os.environ.get('LORA_TTF', '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf')   # шрифт Lora (Google Fonts, OFL)
def _ttf(name):  # Manrope с сайта (woff2) → ttf рядом со скриптом при первом запуске
    out = os.path.join(HERE, name + '.ttf')
    if not os.path.exists(out):
        f = TTFont(os.path.join(HERE, '..', '..', 'docs', 'fonts', name + '.woff2')); f.flavor = None; f.save(out)
    return out
MAN_CYR, MAN_LAT = _ttf('manrope-cyrillic-wght-normal'), _ttf('manrope-latin-wght-normal')
_cmap = {p: set(TTFont(p).getBestCmap()) for p in (MAN_CYR, MAN_LAT, LORA)}
_cache = {}
def font(path, size, wght=None):
    k = (path, size, wght)
    if k not in _cache:
        f = ImageFont.truetype(path, size)
        if wght:
            try: f.set_variation_by_axes([wght])
            except Exception: pass
        _cache[k] = f
    return _cache[k]

class Txt:
    """Текст с подбором шрифта по символу (кириллица / латиница и цифры у Manrope — в разных файлах)."""
    def __init__(self, kind, size, wght=None):
        self.kind, self.size, self.wght = kind, size, wght
    def runs(self, s):
        if self.kind == 'serif': return [(font(LORA, self.size, self.wght), s)]
        out = []
        for ch in s:
            p = MAN_CYR if ord(ch) in _cmap[MAN_CYR] else MAN_LAT
            f = font(p, self.size, self.wght)
            if out and out[-1][0] is f: out[-1] = (f, out[-1][1] + ch)
            else: out.append((f, ch))
        return out
    def width(self, s, track=0):
        return sum(f.getlength(t) for f, t in self.runs(s)) + track * max(0, len(s) - 1)
    def draw(self, d, xy, s, fill, track=0):
        x, y = xy
        for f, t in self.runs(s):
            if track:
                for ch in t: d.text((x, y), ch, font=f, fill=fill); x += f.getlength(ch) + track
            else:
                d.text((x, y), t, font=f, fill=fill); x += f.getlength(t)
    def wrap(self, s, maxw):
        lines, cur = [], ''
        for w in s.split(' '):
            t = (cur + ' ' + w).strip()
            if self.width(t) <= maxw or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        return lines

EYEBROW = Txt('sans', 30, 700)
TITLE = Txt('serif', 66, 500)
CAPTION = Txt('sans', 38, 500)
SMALL = Txt('sans', 30, 600)
BIG = Txt('serif', 96, 500)

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))
def ease_out(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def rgba(c, a): return c + (int(255 * max(0, min(1, a))),)

def text_block(d, lines, txt, x, y, fill, lh, align='left', a=1.0, maxw=W):
    for i, l in enumerate(lines):
        lw = txt.width(l)
        xx = x if align == 'left' else (W - lw) / 2
        txt.draw(d, (xx, y + i * lh), l, rgba(fill, a))
    return y + len(lines) * lh

# ---------- подготовка картинок ----------
def prep(name):
    im = Image.open(IMG + name).convert('RGB')
    bg = im.copy()
    s = max(W / bg.width, H / bg.height) * 1.15
    bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = Image.blend(bg, Image.new('RGB', (W, H), PINE), 0.72)
    return im, bg

WIN = (60, 600, W - 60, 1380)          # окно с инфографикой: 960×780
WIN_W, WIN_H = WIN[2] - WIN[0], WIN[3] - WIN[1]
mask_cache = {}
def round_mask(w, h, r):
    k = (w, h, r)
    if k not in mask_cache:
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); mask_cache[k] = m
    return mask_cache[k]

def segments(d, active, prog):
    """Полоски прогресса как в сторис: 8 уроков."""
    n, gap, x0, x1, y = 8, 10, 60, W - 60, 196
    sw = (x1 - x0 - gap * (n - 1)) / n
    for i in range(n):
        xa = x0 + i * (sw + gap)
        d.rounded_rectangle((xa, y, xa + sw, y + 6), 3, fill=rgba(IVORY, .22))
        f = 1 if i < active else (prog if i == active else 0)
        if f > 0: d.rounded_rectangle((xa, y, xa + sw * f, y + 6), 3, fill=rgba(GOLD_SOFT, .95))

def brand(d, y, a=1.0, center=False):
    s = 'Soul of Home'; f = Txt('serif', 38, 600)
    w = f.width(s) + 26
    x = (W - w) / 2 if center else 60
    d.ellipse((x, y + 16, x + 12, y + 28), fill=rgba(GOLD, a))
    f.draw(d, (x + 26, y), s, rgba(IVORY, a))

# ---------- сцены ----------
def lesson_frame(i, t, assets):
    topic, title, cap, name = LESSONS[i]
    im, bg = assets[i]
    p = t / T_LESSON
    fr = bg.copy().convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # инфографика: высота окна ×1.12, медленный проезд слева направо и лёгкий наезд
    z = 1.12 + 0.05 * ease(p)
    ih = int(WIN_H * z); iw = int(im.width * ih / im.height)
    if iw < WIN_W * 1.04: iw = int(WIN_W * 1.06); ih = int(im.height * iw / im.width)
    big = im.resize((iw, ih), Image.BILINEAR)
    ox = int((iw - WIN_W) * (0.04 + 0.92 * ease(p))); oy = int((ih - WIN_H) * 0.5)
    crop = big.crop((ox, oy, ox + WIN_W, oy + WIN_H))
    # карточка: тень, рамка, появление снизу
    rise = 40 * (1 - ease_out(t / 0.6))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((WIN[0], WIN[1] + 24 + rise, WIN[2], WIN[3] + 24 + rise), 30, fill=(0, 0, 0, 120))
    fr = Image.alpha_composite(fr, sh.filter(ImageFilter.GaussianBlur(26)))
    fr.paste(crop, (WIN[0], int(WIN[1] + rise)), round_mask(WIN_W, WIN_H, 28))
    d.rounded_rectangle((WIN[0], WIN[1] + rise, WIN[2] - 1, WIN[3] - 1 + rise), 28, outline=rgba(GOLD_SOFT, .7), width=2)
    # верх: прогресс, номер урока, заголовок
    segments(d, i, p)
    a1 = ease_out((t - 0.1) / 0.5)
    EYEBROW.draw(d, (60, 248 - 14 * (1 - a1)), f'УРОК {i + 1} ИЗ 8 · {topic.upper()}', rgba(GOLD_SOFT, a1), track=3)
    a2 = ease_out((t - 0.2) / 0.55)
    text_block(d, TITLE.wrap(title, W - 120), TITLE, 60, 304 + 18 * (1 - a2), IVORY, 78, a=a2)
    # низ: главная мысль
    a3 = ease_out((t - 0.55) / 0.6)
    lines = CAPTION.wrap(cap, W - 120)
    y = 1430 + 16 * (1 - a3)
    d.rectangle((60, y + 6, 66, y + 6 + len(lines) * 54 - 14), fill=rgba(GOLD, a3))
    for k, l in enumerate(lines): CAPTION.draw(d, (88, y + k * 54), l, rgba(IVORY, .92 * a3))
    return Image.alpha_composite(fr, ov).convert('RGB')

def intro_frame(t, collage):
    fr = collage.copy().convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a0 = ease_out(t / 0.6)
    brand(d, 330, a0, center=True)
    a1 = ease_out((t - 0.25) / 0.7)
    y = text_block(d, ['8 бесплатных', 'уроков', 'об уюте'], BIG, 0, 620 + 30 * (1 - a1), IVORY, 116, align='center', a=a1)
    a2 = ease_out((t - 0.8) / 0.6)
    sub = 'цвет · свет · текстиль · ручная работа'
    SMALL.draw(d, ((W - SMALL.width(sub, 2)) / 2, y + 40), sub, rgba(GOLD_SOFT, a2), track=2)
    # золотая нить-разделитель
    a3 = ease_out((t - 1.1) / 0.7)
    d.line(((W / 2 - 140 * a3, y + 130), (W / 2 + 140 * a3, y + 130)), fill=rgba(GOLD, .8), width=2)
    a4 = ease_out((t - 1.5) / 0.6)
    s = 'Сохраните, чтобы не потерять'
    CAPTION.draw(d, ((W - CAPTION.width(s)) / 2, 1430), s, rgba(IVORY, .85 * a4))
    return Image.alpha_composite(fr, ov).convert('RGB')

def outro_frame(t, collage):
    fr = collage.copy().convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a1 = ease_out(t / 0.6)
    y = text_block(d, ['Все 8 уроков —', 'бесплатно', 'на сайте'], BIG, 0, 520 + 30 * (1 - a1), IVORY, 116, align='center', a=a1)
    a2 = ease_out((t - 0.5) / 0.6)
    # кнопка-плашка
    s = 'Ссылка в профиле'
    bw = CAPTION.width(s) + 96; bx = (W - bw) / 2; by = y + 70 + 20 * (1 - a2)
    d.rounded_rectangle((bx, by, bx + bw, by + 96), 48, fill=rgba(GOLD, a2))
    CAPTION.draw(d, (bx + 48, by + 22), s, rgba(PINE, a2))
    a3 = ease_out((t - 0.9) / 0.6)
    s2 = 'Вопросы — Нейрокоту в Telegram: @SoulHomeRuBot'
    lines = SMALL.wrap(s2, W - 160)
    for k, l in enumerate(lines): SMALL.draw(d, ((W - SMALL.width(l)) / 2, by + 150 + k * 44), l, rgba(IVORY, .85 * a3))
    a4 = ease_out((t - 1.2) / 0.6)
    brand(d, 1440, a4, center=True)
    return Image.alpha_composite(fr, ov).convert('RGB')

def make_collage(assets):
    """Фон заставки и финала: мозаика из обложек уроков, сильно притушенная."""
    c = Image.new('RGB', (W, H), PINE)
    cw, ch = W // 2, H // 4
    for k in range(8):
        im = assets[k][0]
        s = max(cw / im.width, ch / im.height)
        t = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        t = t.crop(((t.width - cw) // 2, (t.height - ch) // 2, (t.width - cw) // 2 + cw, (t.height - ch) // 2 + ch))
        c.paste(t, ((k % 2) * cw, (k // 2) * ch))
    c = c.filter(ImageFilter.GaussianBlur(28))
    c = Image.blend(c, Image.new('RGB', (W, H), PINE), 0.78)
    # мягкое золотое свечение
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((140, 520, 940, 1300), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new('RGB', (W, H), (90, 72, 34)), c, glow)

# ---------- таймлайн ----------
def build(out, preview=None):
    assets = [prep(l[3]) for l in LESSONS]
    collage = make_collage(assets)
    scenes = [('intro', T_INTRO)] + [('lesson', T_LESSON)] * 8 + [('outro', T_OUTRO)]
    starts, acc = [], 0.0
    for k, (_, dur) in enumerate(scenes):
        starts.append(acc); acc += dur - (T_X if k < len(scenes) - 1 else 0)
    total = acc
    def render(k, t):
        kind = scenes[k][0]
        if kind == 'intro': return intro_frame(t, collage)
        if kind == 'outro': return outro_frame(t, collage)
        return lesson_frame(k - 1, t, assets)
    def frame_at(T):
        k = max(i for i, s in enumerate(starts) if s <= T + 1e-9)
        t = T - starts[k]
        img = render(k, t)
        if k + 1 < len(scenes) and T >= starts[k + 1] - 1e-9:
            pass
        nxt = k + 1
        if nxt < len(scenes) and T > starts[nxt] - 1e-9:
            pass
        # растворение: если идёт хвост сцены k и начало сцены k+1
        if nxt < len(scenes) and T >= starts[nxt]:
            pass
        return img
    if preview is not None:
        return [(T, frame_at_x(T, scenes, starts, render)) for T in preview], total
    n = int(round(total * FPS))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', str(FPS),
           '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        pr.stdin.write(frame_at_x(f / FPS, scenes, starts, render).tobytes())
    pr.stdin.close(); pr.wait()
    return total

def frame_at_x(T, scenes, starts, render):
    k = max(i for i, s in enumerate(starts) if s <= T + 1e-9)
    img = render(k, T - starts[k])
    # предыдущая сцена ещё растворяется?
    if k > 0:
        tp = T - starts[k - 1]
        tail = scenes[k - 1][1] - tp          # сколько осталось от предыдущей
        if tail > 0:
            prev = render(k - 1, tp)
            a = ease(1 - tail / T_X)          # 0 → 1 за время перехода
            img = Image.blend(prev, img, a)
    return img

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        frames, total = build(None, preview=[1.6, 3.4, 5.6, 7.0, 21.0, 36.0, total_guess := 40.0])
        for T, im in frames: im.save(os.path.join(HERE, f'prev-{T:05.1f}.jpg'), quality=88)
        print('total', total)
    else:
        print('total', build(os.path.join(HERE, 'soul-of-home-reels-8-urokov.mp4')))
