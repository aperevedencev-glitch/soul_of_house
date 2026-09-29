#!/usr/bin/env bash
# Установка бота Soul of Home (Нейрокот) на сервер Ubuntu/Debian одной командой:
#   sudo bash install.sh
# Скрипт ставит Python, копирует бота в /opt/soulhome-bot, спрашивает токены и включает автозапуск.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then echo "Запустите через sudo: sudo bash install.sh"; exit 1; fi
SRC="$(cd "$(dirname "$0")" && pwd)"
DST=/opt/soulhome-bot

echo "== 1/5 Устанавливаю Python =="
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip >/dev/null

echo "== 2/5 Копирую файлы в $DST =="
id soulhome >/dev/null 2>&1 || useradd -r -s /usr/sbin/nologin soulhome
mkdir -p "$DST"
cp "$SRC"/bot.py "$SRC"/funnel.py "$SRC"/knowledge.py "$SRC"/requirements.txt "$SRC"/neurocat.jpg "$DST"/
[ -f "$DST/.env" ] || cp "$SRC/.env.example" "$DST/.env"

echo "== 3/5 Ставлю библиотеки =="
python3 -m venv "$DST/venv"
"$DST/venv/bin/pip" install -q --upgrade pip
"$DST/venv/bin/pip" install -q -r "$DST/requirements.txt"

echo "== 4/5 Настройки (Enter — оставить как есть) =="
setval() {  # setval КЛЮЧ ЗНАЧЕНИЕ
  if grep -q "^$1=" "$DST/.env"; then sed -i "s|^$1=.*|$1=$2|" "$DST/.env"; else echo "$1=$2" >> "$DST/.env"; fi
}
read -r -p "Токен бота от @BotFather: " v;               [ -n "$v" ] && setval BOT_TOKEN "$v"
read -r -p "Ключ OpenRouter (sk-or-..., можно пропустить): " v; [ -n "$v" ] && setval AI_API_KEY "$v"
read -r -p "ID чата мастера (можно пропустить и узнать потом командой /myid): " v; [ -n "$v" ] && setval ADMIN_CHAT_ID "$v"
chown -R soulhome "$DST"
chmod 600 "$DST/.env"

echo "== 5/5 Включаю автозапуск =="
cp "$SRC/soulhome-bot.service" /etc/systemd/system/soulhome-bot.service
systemctl daemon-reload
systemctl enable --now soulhome-bot
sleep 3
systemctl --no-pager --lines=8 status soulhome-bot || true

echo
echo "Готово. Напишите боту /start в Telegram."
echo "Логи:        sudo journalctl -u soulhome-bot -f"
echo "Настройки:   sudo nano $DST/.env   → затем sudo systemctl restart soulhome-bot"
