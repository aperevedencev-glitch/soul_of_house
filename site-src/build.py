"""Сборка сайта Soul of Home.

    python3 site-src/build.py

Берёт содержимое страниц из site-src/pages/*.html, добавляет общий <head> (SEO, иконки, шрифты,
PWA, аналитика), шапку, подвал и пишет готовые страницы в docs/, а также sitemap.xml и robots.txt.
Стили, скрипты, картинки и шрифты правятся прямо в docs/ (styles.css, site.js, img/ …).
Домен для canonical/og/sitemap: переменная SOH_DOMAIN (по умолчанию — GitHub Pages).
"""
import os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent          # корень репозитория
SRC = ROOT / 'site-src' / 'pages'                              # содержимое страниц (без шапки, подвала и <head>)
OUT = pathlib.Path(os.environ.get('SOH_OUT', ROOT / 'docs'))  # готовый сайт

import re as _re
FONT_FACES = _re.sub(r'url\(([^)]+)\)', r'url(fonts/\1)', _re.sub(r'/\*.*?\*/\s*', '', (ROOT / 'docs' / 'fonts' / 'fonts.css').read_text(), flags=_re.S)).replace('\n', '')
FONTS = ('<link rel="icon" href="favicon.ico" sizes="any">\n'
         '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">\n'
         '<link rel="icon" type="image/png" sizes="512x512" href="icon-512.png">\n'
         '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
         '<link rel="manifest" href="manifest.json">\n'
         '<meta name="application-name" content="Soul of Home">\n'
         '<meta name="mobile-web-app-capable" content="yes">\n'
         '<meta name="apple-mobile-web-app-capable" content="yes">\n'
         '<meta name="apple-mobile-web-app-title" content="Soul of Home">\n'
         '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
         '<meta name="format-detection" content="telephone=no">\n'
         '<meta name="theme-color" content="#0E1C16">\n'
         '<link rel="preload" href="fonts/manrope-cyrillic-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
         '<link rel="preload" href="fonts/fraunces-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
         '<style>' + FONT_FACES + '</style>\n<link rel="stylesheet" href="styles.css">')

# ===== Домен сайта (для sitemap.xml и robots.txt): без слеша в конце =====
SITE_DOMAIN = os.environ.get('SOH_DOMAIN', 'https://aperevedencev-glitch.github.io/soul_of_house').rstrip('/')  # адрес GitHub Pages; при своём домене замените

# ===== Аналитика: впишите сюда номер счётчика и ID потока, затем пересоберите сайт =====
YM_ID = ''   # (не используется: номера задаются в analytics-config.js рядом с сайтом)
GA_ID = ''

def analytics_head():
    return f"""<script src="analytics-config.js" defer></script>
<!-- Яндекс.Метрика -->
<script>
document.addEventListener('DOMContentLoaded', function(){{ (function(id){{ if(!id) return;
  (function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();
  for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
  k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
  (window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
  ym(Number(id), 'init', {{clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true}});
}})((window.SOH_ANALYTICS || {{}}).ym); }});
</script>
<!-- /Яндекс.Метрика -->
<!-- Google Analytics 4 -->
<script>
document.addEventListener('DOMContentLoaded', function(){{ (function(id){{ if(!id) return;
  var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function(){{ dataLayer.push(arguments); }};
  gtag('js', new Date()); gtag('config', id);
}})((window.SOH_ANALYTICS || {{}}).ga); }});
</script>
<!-- /Google Analytics 4 -->
<script>
// цели: SOH_goal('apply') — одинаково для Метрики и GA4
window.SOH_goal = function(name){{ try{{ var c = window.SOH_ANALYTICS || {{}}; if(window.ym && c.ym) ym(Number(c.ym), 'reachGoal', name); if(window.gtag && c.ga) gtag('event', name); }}catch(e){{}} }};
</script>"""

def analytics_body():
    return f'<noscript><div><img src="https://mc.yandex.ru/watch/{YM_ID}" style="position:absolute; left:-9999px;" alt=""></div></noscript>\n' if YM_ID else ''


# ===== СТРАНИЦЫ САЙТА — единственное место, где они перечислены =====
# Новая страница: положите site-src/pages/<файл>.html и добавьте строку сюда.
# key/файл, заголовок вкладки, пункт меню (None — не показывать в меню), описание для поиска, (приоритет, частота) для sitemap (None — не в sitemap)
PAGE_TABLE = [
    ('index', 'Soul of Home — новогодние шары ручной работы и школа уюта', 'Главная',
     'Мастерская и школа ручной работы Soul of Home: авторские новогодние шары из бархата, кружева и жемчуга, курсы и бесплатные уроки об уюте в доме.', ('1.0', 'weekly')),
    ('raboty', 'Мои работы · Soul of Home', 'Мои работы',
     'Коллекция из 12 новогодних шаров ручной работы: бархат, кружево, жемчуг и вышивка. Шары 8 см, заказ под цвет вашей ёлки или интерьера.', ('0.9', 'monthly')),
    ('obuchenie', 'Обучение · Soul of Home', 'Обучение',
     'Курсы Soul of Home: бархатный шар для начинающих, вышивка и жемчуг, своя коллекция, дизайн уютного дома и праздничный интерьер.', ('0.8', 'monthly')),
    ('uroki', 'Уроки · Soul of Home', 'Уроки',
     'Бесплатные уроки об уюте: палитра 60·30·10, тёплый свет, правило трёх текстур, первый бархатный шар, объёмная ёлка и хранение игрушек.', ('0.8', 'weekly')),
    ('kompanii', 'Для компаний · Soul of Home', 'Для компаний',
     'Бесплатный чек-лист «Офис к новогоднему корпоративу за 7 шагов» и концепция оформления офиса под ключ от студии Soul of Home.', ('0.9', 'monthly')),
    ('o-nas', 'О нас · Soul of Home', 'О нас',
     'О мастерской Soul of Home: миссия, команда и цифры — 12 авторских шаров, 6 программ обучения и 8 бесплатных уроков об уюте.', ('0.6', 'monthly')),
    ('profile', 'Профиль · Soul of Home', None,   # личный кабинет: иконка в шапке, закрыт от поиска
     'Личный кабинет Soul of Home: имя, email и дата регистрации.', None),
]
def href(key): return './' if key == 'index' else key + '.html'
NAV = [(href(k), m, k) for k, t, m, d, s in PAGE_TABLE if m]
DESC = {k: d for k, t, m, d, s in PAGE_TABLE}
PAGES = {k: t for k, t, m, d, s in PAGE_TABLE}
FOOT_LINKS = ''.join(f'<a href="{h}">{m}</a>' for h, m, k in NAV) + '<a href="profile.html">Профиль</a><a href="https://t.me/SoulHomeRuBot" target="_blank" rel="noopener">Telegram</a>'


PRELOADER = '''<div class="preloader" id="preloader" aria-hidden="true"><div class="pl-inner"><span class="pl-ring"></span><span class="pl-logo">Soul of Home</span></div></div>
<script>(function(){var seen=false;try{seen=sessionStorage.getItem('soh-seen')==='1';sessionStorage.setItem('soh-seen','1');}catch(e){}var p=document.getElementById('preloader');if(seen){p.parentNode.removeChild(p);return;}var done=false;function hide(){if(done)return;done=true;p.classList.add('pl-done');setTimeout(function(){if(p.parentNode)p.parentNode.removeChild(p);},600);}if(document.readyState==='complete')hide();else window.addEventListener('load',hide);setTimeout(hide,4000);})();</script>
'''

NOINDEX = '<meta name="robots" content="noindex">'

def seo_head(key, title):
    url = SITE_DOMAIN + '/' + ('' if key == 'index' else key + '.html')
    img = SITE_DOMAIN + '/img/og-image.jpg'
    d = DESC.get(key, DESC['index'])
    lcp = ('<link rel="preload" as="image" href="img/cat-mascot-560.webp" imagesrcset="img/cat-mascot-360.webp 360w, img/cat-mascot-560.webp 560w, img/cat-mascot.webp 900w" imagesizes="(max-width: 820px) 260px, 440px" fetchpriority="high">\n' if key == 'index' else '')
    return (f'<meta name="description" content="{d}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Soul of Home">\n<meta property="og:locale" content="ru_RU">\n'
            f'<meta property="og:title" content="{title}">\n<meta property="og:description" content="{d}">\n<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{img}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="Soul of Home — мастерская и школа ручной работы">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{title}">\n<meta name="twitter:description" content="{d}">\n<meta name="twitter:image" content="{img}">\n'
            f'<meta name="soh-sw" content="sw.js">\n' + lcp)

def header(cur):
    AC = ' aria-current="page"'
    links = '\n'.join(f'      <a href="{h}"{AC if k == cur else ""}>{t}</a>' for h, t, k in NAV)
    return PRELOADER + f'''<header class="site">
  <div class="nav-inner">
    <a class="logo" href="./"><span class="mark"></span> Soul of Home</a>
    <nav class="nav-links" aria-label="Разделы сайта">
{links}
    </nav>
    <div class="nav-right">
      <a class="nav-profile" href="profile.html" aria-label="Мой профиль"{AC if cur == "profile" else ""}><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c1.5-3.6 4.4-5.4 8-5.4s6.5 1.8 8 5.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></a>
      <a class="nav-cta" href="obuchenie.html#apply">Записаться</a>
      <button class="menu-btn" type="button" aria-label="Меню" aria-expanded="false"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M3 5h12M3 9h12M3 13h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
    </div>
  </div>
</header>'''

FOOTER = f'''<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="logo" href="./"><span class="mark"></span> Soul of Home</a>
        <p>Мастерская и школа ручной работы для уютного дома</p>
      </div>
      <nav class="foot-links" aria-label="Разделы сайта">
        {FOOT_LINKS}
      </nav>
    </div>
    <p class="foot-note">© 2026 Soul of Home · Все изделия и фотографии — авторская ручная работа</p>
  </div>
</footer>
<script src="site.js" charset="utf-8"></script>'''

for key, title in PAGES.items():
    body = (SRC / f'{key}.html').read_text()
    extra = ''
    if '<!--SCRIPT-->' in body:
        body, extra = body.split('<!--SCRIPT-->')
    inner = f'{header(key)}\n{body}\n{FOOTER}\n{extra}'
    robots = NOINDEX if key == 'profile' else ''
    html = f'<!DOCTYPE html>\n<!-- Сгенерировано site-src/build.py из site-src/pages/{key}.html — правьте исходник, не этот файл -->\n<html lang="ru">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>{title}</title>{robots}\n{seo_head(key, title)}{FONTS}\n{analytics_head()}\n</head>\n<body>\n{analytics_body()}{inner}\n</body>\n</html>\n'
    (OUT / f'{key}.html').write_text(html)
    print('built', key)

# ---------- sitemap.xml и robots.txt ----------
import datetime
from zoneinfo import ZoneInfo
TODAY = datetime.datetime.now(ZoneInfo('Europe/Moscow')).date().isoformat()  # дата по Москве
PRIO = {'index': ('1.0', 'weekly'), 'raboty': ('0.9', 'monthly'), 'kompanii': ('0.9', 'monthly'), 'obuchenie': ('0.8', 'monthly'), 'uroki': ('0.8', 'weekly'), 'o-nas': ('0.6', 'monthly')}
urls = []
for key in PAGES:
    if key not in PRIO: continue  # личный кабинет не отдаём поисковикам
    loc = SITE_DOMAIN + '/' + ('' if key == 'index' else key + '.html')
    pr, fr = PRIO[key]
    urls.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{fr}</changefreq>\n    <priority>{pr}</priority>\n  </url>')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
(OUT / 'robots.txt').write_text(f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/
Disallow: /test/
Disallow: /profile.html

Sitemap: {SITE_DOMAIN}/sitemap.xml
""")
print('built sitemap.xml, robots.txt')
