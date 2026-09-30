#!/usr/bin/env bash
# Сборка сайта для reg.ru: ./build.sh https://ваш-домен.ru
# Результат: public_html/ (залить содержимое в корень сайта) и soul-of-home-regru.zip
set -e
DOMAIN="${1:?Укажите домен: ./build.sh https://ваш-домен.ru}"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/../.."
rm -rf "$HERE/public_html" "$HERE/soul-of-home-regru.zip"
cp -r "$ROOT/docs" "$HERE/public_html"
rm -f "$HERE/public_html/.nojekyll" "$HERE/public_html/fonts/fonts.css.bak"
DOMAIN="${DOMAIN%/}"; OLD="https://aperevedencev-glitch.github.io/soul_of_house"
# адрес сайта в canonical, og:url, og:image, sitemap.xml, robots.txt
find "$HERE/public_html" -maxdepth 1 -type f \( -name '*.html' -o -name '*.xml' -o -name '*.txt' \) \
  -exec sed -i "s#${OLD}#${DOMAIN}#g" {} +
cp "$HERE/.htaccess" "$HERE/404.html" "$HERE/public_html/"
(cd "$HERE/public_html" && zip -qr9 "$HERE/soul-of-home-regru.zip" . -x '*.DS_Store')
echo "Готово: $HERE/soul-of-home-regru.zip ($DOMAIN)"
