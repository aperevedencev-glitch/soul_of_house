// Soul of Home — общие скрипты сайта
(function(){
  // ----- мобильное меню -----
  var btn = document.querySelector('.menu-btn');
  var links = document.querySelector('.nav-links');
  if(btn && links){
    btn.addEventListener('click', function(){
      var open = links.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
    links.addEventListener('click', function(e){
      if(e.target.closest('a')){ links.classList.remove('open'); btn.setAttribute('aria-expanded','false'); }
    });
  }

  // ----- безопасное хранилище (может быть недоступно) -----
  window.SOH_store = {
    get: function(k, def){ try{ var v = localStorage.getItem(k); return v ? JSON.parse(v) : def; }catch(e){ return def; } },
    set: function(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  };

  // ----- копирование текста -----
  window.SOH_copy = function(button, text, label){
    function done(msg){ button.textContent = msg; setTimeout(function(){ button.textContent = label; }, 2200); }
    try{
      navigator.clipboard.writeText(text).then(function(){ done('Скопировано ✓'); }, function(){ done('Выделите текст вручную'); });
    }catch(e){ done('Выделите текст вручную'); }
  };

  // ----- фильтр по чипам -----
  window.SOH_filter = function(bar, items, attr, onChange){
    bar.addEventListener('click', function(e){
      var chip = e.target.closest('.chip'); if(!chip) return;
      bar.querySelectorAll('.chip').forEach(function(c){ c.classList.remove('active'); c.setAttribute('aria-pressed','false'); });
      chip.classList.add('active'); chip.setAttribute('aria-pressed','true');
      var f = chip.dataset.filter, shown = 0;
      items().forEach(function(it){
        var tags = (it.getAttribute(attr) || '').split(' ');
        var match = f === 'all' || tags.indexOf(f) !== -1;
        it.hidden = !match; if(match) shown++;
      });
      if(onChange) onChange(shown);
    });
  };

  // ----- форма записи: выбор курса → Telegram-бот -----
  var form = document.getElementById('applyForm');
  if(form){
    var success = document.getElementById('successState');
    var intro = document.getElementById('formIntro');
    function checkRadio(){
      var wrap = form.querySelector('[data-field="course"]');
      var ok = !!form.querySelector('input[name="course"]:checked');
      wrap.classList.toggle('has-error', !ok); return ok;
    }
    form.addEventListener('change', checkRadio);
    form.addEventListener('submit', function(e){
      e.preventDefault();
      if(!checkRadio()) return;
      var r = form.querySelector('input[name="course"]:checked');
      document.getElementById('successCourse').textContent = r.value;
      document.getElementById('successTg').href = 'https://t.me/SoulHomeRuBot?start=' + r.dataset.tg;
      form.hidden = true; intro.hidden = true; success.hidden = false;
      if(window.SOH_goal) SOH_goal('apply_course');
    });
  }
})();

// ===== Нейрокот: ИИ-помощник Soul of Home =====
(function(){
  var TG = 'https://t.me/SoulHomeRuBot';
  var RULES = [
    'Ты — Нейрокот, пушистый ИИ-помощник и талисман мастерской и школы ручной работы Soul of Home.',
    'Ты помогаешь посетителям сайта: отвечаешь на вопросы о дизайне уютного дома, о создании новогодних шаров и декора ручной работы, о коллекции и программах обучения, подсказываешь, с чего начать.',
    'Стиль: тёплый, дружелюбный, спокойный, чуть-чуть кошачьего обаяния (можно изредка «мур»), но по делу. Пиши по-русски, коротко: 2–6 предложений или короткий список с «—». Без Markdown-разметки, без заголовков и звёздочек.',
    'Не выдумывай цены, даты стартов, сроки доставки и наличие: для этого предлагай оставить заявку на странице «Обучение» или написать в Telegram-бот @SoulHomeRuBot. Если вопрос не про дом, уют, рукоделие или Soul of Home — мягко верни разговор к этим темам.',
    '',
    'ЧТО ЕСТЬ НА САЙТЕ.',
    'Страницы: Главная; «Мои работы» (коллекция шаров); «Обучение» (программы и форма заявки); «Уроки» (бесплатные материалы).',
    'Коллекция «Новогодние шары»: 12 авторских моделей, все 8 см в диаметре, 100% ручная работа. Шар с камеей и кружевом (айвори, золото); с белыми цветами и кисточкой; с белым бантом и кисточкой; с балериной (полимерная глина, жемчуг); с цветами и жемчугом; из бархата и вышивки (изумруд, красный); с бархатной отделкой (красный); с изумрудным бантом; бархатный с блеском (изумруд, глиттер); бархатный с бантом (изумруд); из смешанных материалов (красный, шнур); винтажный (красный бархат, золотая вышивка). Материалы: бархат, кружево, атлас, жемчуг, стразы, кристаллы, металлическая фурнитура. Заказ шара под цвет ёлки или интерьера — через @SoulHomeRuBot.',
    'Программы обучения: 1) «Бархатный шар» — для начинающих, 3 урока: основа 8 см, раскрой, обтяжка без морщин, бант, кисточка, фурнитура. Лучший старт для новичка. 2) «Вышивка, жемчуг и кружево» — средний уровень, 5 уроков: объёмная вышивка металлизированной нитью, жемчуг и стразы, камея, объёмные цветы. 3) «Своя авторская коллекция» — продвинутый, 4 урока: концепция, палитра серии, фотосъёмка. 4) «Дизайн уютного дома» — для всех, 6 уроков: палитра 60/30/10, сценарии света, текстиль и композиция. 5) «Праздничный интерьер» — 4 урока: ёлка как композиция, венок, сервировка. 6) «От хобби к делу» — личный разбор 45 минут для мастеров: формула цены, портфолио, каналы продаж (ярмарки, маркетплейсы, опт, корпоративные подарки).',
    'Как проходит обучение: заявка → список материалов (для «Бархатного шара» можно заказать набор) → видеоуроки в своём темпе, доступ остаётся → фото готовой работы и личная обратная связь. Опыт не обязателен. Стоимость и даты мастер присылает в ответ на заявку.',
    'Бесплатные уроки: палитра 60/30/10; тёплый свет 2700–3000 K и три уровня освещения (общий, локальный, акцентный), CRI 90+; правило трёх текстур (гладкое, мягкое, рельефное); первый бархатный шар (мастер-класс в 6 шагов: материалы — пенопластовая основа 8 см, бархат ~30×30 см, прозрачный клей для ткани, декор, шапочка с петлёй и лента; обтяжка: круг бархата ⌀ 26–28 см, клей тонким слоем, натягивать от низа вверх по кругу, излишки собрать наверху под шапочку; декор — вышивка металлизированной нитью, бусины, жемчуг, стразы; шапочка на каплю клея, лента и бант; проверить крепление и дать высохнуть; советы: качественный бархат, пенопластовая основа, экспериментировать с цветом); как нарядить ёлку (расправить ветки, гирлянда от ствола, ~100 лампочек на 30 см высоты, крупные шары вглубь, авторские снаружи на уровне глаз); подушки и пледы (нечётное число, разные размеры, один узор); хранение игрушек (папиросная бумага, коробка с ячейками, сухое место, силикагель, не мочить вышивку); упаковка подарка ручной работы с карточкой-историей.',
    'Когда уместно, ссылайся на страницы сайта по названию и предлагай следующий шаг.'
  ].join('\n');
  var SUGS = ['С какого курса начать новичку?', 'Как сделать первый бархатный шар?', 'Как подобрать палитру для ёлки?', 'Как сделать комнату уютнее без ремонта?'];
  var CAT_SVG_SEND = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var CAT_SVG_STOP = '<svg width="14" height="14" viewBox="0 0 14 14"><rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/></svg>';

  var sample = null, sampleChecked = false, disabled = false;
  var turns = [], ctl = null, busy = false, panel, log, input, sendBtn, sugs, fab;

  function getSample(){
    if(sampleChecked) return Promise.resolve(sample);
    if(!window.claude || !window.claude.use){ sampleChecked = true; return Promise.resolve(null); }
    return window.claude.use('sample').then(function(s){ sample = s; sampleChecked = true; return s; }, function(){ sampleChecked = true; return null; });
  }

  function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
  function add(cls, text){ var m = el('div', 'nc-msg ' + cls, text); log.appendChild(m); log.scrollTop = log.scrollHeight; return m; }
  function noteTelegram(msg){
    var m = add('note', msg + ' ');
    var a = el('a', '', 'Написать в Telegram @SoulHomeRuBot'); a.href = TG; a.target = '_blank'; a.rel = 'noopener';
    m.appendChild(a); log.scrollTop = log.scrollHeight;
  }

  function build(){
    panel = el('div', 'nc-panel'); panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Чат с Нейрокотом'); panel.hidden = true;
    panel.innerHTML =
      '<div class="nc-head"><img src="img/neurocat-face.jpg" alt=""><div><div class="nc-title">Нейрокот</div><div class="nc-status"><span class="dot"></span>ИИ-помощник Soul of Home</div></div>' +
      '<button class="nc-x" type="button" aria-label="Закрыть чат"><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg></button></div>' +
      '<div class="nc-log" aria-live="polite"></div><div class="nc-sugs"></div>' +
      '<form class="nc-form"><label for="ncInput" class="sr-only" style="position:absolute;left:-9999px;">Ваш вопрос</label><textarea id="ncInput" rows="1" placeholder="Спросите про уют, шары или курсы…"></textarea><button class="nc-send" type="submit" aria-label="Отправить">' + CAT_SVG_SEND + '</button></form>' +
      '<div class="nc-tg">Ответы генерирует ИИ. Заказы и оплата — в <a href="' + TG + '" target="_blank" rel="noopener">@SoulHomeRuBot</a></div>';
    document.body.appendChild(panel);
    log = panel.querySelector('.nc-log'); input = panel.querySelector('textarea'); sendBtn = panel.querySelector('.nc-send'); sugs = panel.querySelector('.nc-sugs');
    add('bot', 'Мур, привет! Я Нейрокот, помощник мастерской Soul of Home. Спросите меня про новогодние шары, уют в доме или о том, какой курс вам подойдёт.');
    SUGS.forEach(function(q){ var b = el('button', '', q); b.type = 'button'; b.addEventListener('click', function(){ ask(q); }); sugs.appendChild(b); });
    panel.querySelector('.nc-x').addEventListener('click', close);
    panel.querySelector('form').addEventListener('submit', function(e){ e.preventDefault(); if(busy){ if(ctl) ctl.abort(); return; } ask(input.value); });
    input.addEventListener('keydown', function(e){ if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); if(!busy) ask(input.value); } });
    input.addEventListener('input', function(){ input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 120) + 'px'; });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && !panel.hidden) close(); });

    fab = el('button', 'nc-fab'); fab.type = 'button'; fab.setAttribute('aria-label', 'Открыть чат с Нейрокотом');
    fab.innerHTML = '<img src="img/neurocat-face.jpg" alt=""><span>Спросить Нейрокота</span>';
    fab.addEventListener('click', function(){ open(); if(window.SOH_goal) SOH_goal('chat_open'); });
    document.body.appendChild(fab);
  }

  function setBusy(v){
    busy = v; sendBtn.classList.toggle('stop', v);
    sendBtn.innerHTML = v ? CAT_SVG_STOP : CAT_SVG_SEND;
    sendBtn.setAttribute('aria-label', v ? 'Остановить ответ' : 'Отправить');
  }

  function ask(q){
    q = (q || '').trim(); if(!q || busy) return;
    input.value = ''; input.style.height = 'auto'; sugs.hidden = true;
    add('me', q);
    if(disabled){ noteTelegram('Сейчас я не могу ответить здесь.'); return; }
    var bubble = add('bot wait', 'Нейрокот думает…');
    setBusy(true);
    getSample().then(function(s){
      if(!s){ disabled = true; bubble.remove(); noteTelegram('В этом окне ИИ-чат недоступен, но я отвечу в Telegram.'); setBusy(false); return; }
      turns.push({ role: 'user', content: q });
      if(turns.length > 12) turns = turns.slice(-12);
      while(turns.length && turns[0].role !== 'user') turns.shift();
      ctl = new AbortController();
      return s([{ role: 'user', content: RULES }].concat(turns), {
        cache: false, modelTier: 'quick', signal: ctl.signal,
        onText: function(u){ bubble.classList.remove('wait'); bubble.textContent = u.text; log.scrollTop = log.scrollHeight; }
      }).then(function(r){
        turns.push({ role: 'assistant', content: r.text });
      }, function(e){
        var code = e && e.code;
        if(e && e.text){ bubble.classList.remove('wait'); bubble.textContent = e.text; } else bubble.remove();
        turns.pop();
        if(code === 'cancelled') return;
        if(['not_granted','sampling_disabled','not_declared','capability_disabled','capability_removed'].indexOf(code) !== -1){ disabled = true; noteTelegram('Без разрешения на ИИ я не смогу ответить здесь, но с радостью отвечу в Telegram.'); }
        else if(code === 'rate_limited') add('note', 'Слишком много вопросов подряд. Передохнём минутку и попробуем снова.');
        else if(code === 'session_expired') add('note', 'Нужно заново войти в аккаунт Claude, чтобы продолжить.');
        else if(code === 'refused') add('note', 'На этот вопрос я не отвечу. Давайте поговорим про уют, шары или курсы?');
        else add('note', 'Связь прервалась. Попробуйте отправить вопрос ещё раз.');
      });
    }).then(function(){ setBusy(false); input.focus(); });
  }

  function open(){ if(!panel) build(); panel.hidden = false; fab.hidden = true; setTimeout(function(){ input.focus(); }, 60); }
  function close(){ panel.hidden = true; fab.hidden = false; }

  function init(){
    build(); getSample();
    var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    document.querySelectorAll('[data-neurocat]').forEach(function(t){
      t.addEventListener('click', open);
      if(canHover){
        var timer;
        t.addEventListener('mouseenter', function(){ timer = setTimeout(open, 450); });
        t.addEventListener('mouseleave', function(){ clearTimeout(timer); });
      }
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

// ===== Анимации появления, прогресс чтения, кнопка «Наверх» =====
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  // 1) блоки и карточки: плавно снизу вверх, карточки в сетке — по очереди через 0.1s, один раз
  var GRIDS = '.modules, .works-strip, .proof-grid, .compare, .hero-stats, .foot-grid, .gallery, .lessons, .b2b-grid';
  if('IntersectionObserver' in window && !reduce){
    document.documentElement.classList.add('rv-on');
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if(e.isIntersecting){ var t = e.target; t.classList.add('rv-in'); io.unobserve(t);
        // после появления снимаем классы анимации, чтобы работали обычные hover-эффекты
        var d = parseFloat(t.style.getPropertyValue('--rv-delay')) || 0;
        setTimeout(function(){ t.classList.remove('rv', 'rv-in'); t.style.removeProperty('--rv-delay'); t.dataset.rvDone = '1'; }, 700 + d * 1000); } });
    }, {rootMargin: '0px 0px -8% 0px', threshold: 0.08});
    var mark = function(el, delay){ if(el.classList.contains('rv') || el.dataset.rvDone) return; el.classList.add('rv'); if(delay) el.style.setProperty('--rv-delay', delay + 's'); io.observe(el); };
    var scan = function(root){
      (root || document).querySelectorAll('main section .wrap > *, body > section .wrap > *, .page > section .wrap > *, .lm-sec .wrap > *').forEach(function(el){
        if(el.matches(GRIDS)){ Array.prototype.forEach.call(el.children, function(ch, i){ mark(ch, Math.min(i, 8) * 0.1); }); }
        else mark(el, 0);
      });
    };
    scan();
    window.SOH_reveal = scan; // для карточек, которые скрипт добавляет позже (галерея)
    // галерея «Мои работы» строится скриптом — отмечаем её карточки, когда они появились
    var gal = document.getElementById('gallery');
    if(gal){ new MutationObserver(function(){ Array.prototype.forEach.call(gal.children, function(ch, i){ mark(ch, (i % 4) * 0.1); }); }).observe(gal, {childList: true}); Array.prototype.forEach.call(gal.children, function(ch, i){ mark(ch, (i % 4) * 0.1); }); }
  }

  // 2) прогресс чтения под шапкой
  var header = document.querySelector('header.site');
  var bar = null;
  if(header){ bar = document.createElement('div'); bar.className = 'read-progress'; bar.setAttribute('aria-hidden', 'true'); header.appendChild(bar); }

  // 3) кнопка «Наверх»
  var top = document.createElement('button');
  top.type = 'button'; top.className = 'to-top'; top.setAttribute('aria-label', 'Наверх');
  top.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  top.addEventListener('click', function(){ window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'}); });
  document.body.appendChild(top);

  var ticking = false;
  function update(){
    ticking = false;
    var y = window.scrollY || document.documentElement.scrollTop;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if(bar) bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    top.classList.toggle('show', y > 400);
    top.tabIndex = y > 400 ? 0 : -1;
  }
  window.addEventListener('scroll', function(){ if(!ticking){ ticking = true; requestAnimationFrame(update); } }, {passive: true});
  window.addEventListener('resize', update);
  update();
})();

// ===== Слайдер отзывов: автопрокрутка 4 с, точки, стрелки, пауза при наведении, свайп =====
(function(){
  document.querySelectorAll('[data-slider]').forEach(function(root){
    var track = root.querySelector('.sl-track'), slides = track.children, n = slides.length, i = 0, timer = null, paused = false;
    var dotsBox = root.querySelector('.sl-dots'), reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(n < 2) return;
    for(var k = 0; k < n; k++){ (function(k){ var b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', 'Отзыв ' + (k + 1) + ' из ' + n); b.addEventListener('click', function(){ go(k); restart(); }); dotsBox.appendChild(b); })(k); }
    function go(k){
      i = (k + n) % n; track.style.transform = 'translateX(' + (-100 * i) + '%)';
      Array.prototype.forEach.call(slides, function(s, j){ s.setAttribute('aria-hidden', j === i ? 'false' : 'true'); });
      Array.prototype.forEach.call(dotsBox.children, function(d, j){ d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    }
    function start(){ if(reduce || timer) return; timer = setInterval(function(){ if(!paused && !document.hidden) go(i + 1); }, 4000); }
    function restart(){ clearInterval(timer); timer = null; start(); }
    root.querySelector('.sl-prev').addEventListener('click', function(){ go(i - 1); restart(); });
    root.querySelector('.sl-next').addEventListener('click', function(){ go(i + 1); restart(); });
    root.addEventListener('mouseenter', function(){ paused = true; });
    root.addEventListener('mouseleave', function(){ paused = false; });
    root.addEventListener('focusin', function(){ paused = true; });
    root.addEventListener('focusout', function(){ paused = false; });
    root.addEventListener('keydown', function(e){ if(e.key === 'ArrowLeft'){ go(i - 1); restart(); } if(e.key === 'ArrowRight'){ go(i + 1); restart(); } });
    // свайп пальцем
    var vp = root.querySelector('.sl-viewport'), x0 = null, y0 = 0, dx = 0, horiz = null;
    vp.addEventListener('touchstart', function(e){ x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; dx = 0; horiz = null; paused = true; }, {passive: true});
    vp.addEventListener('touchmove', function(e){
      if(x0 === null) return; dx = e.touches[0].clientX - x0; var dy = e.touches[0].clientY - y0;
      if(horiz === null && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) horiz = Math.abs(dx) > Math.abs(dy);
      if(horiz){ track.classList.add('dragging'); track.style.transform = 'translateX(calc(' + (-100 * i) + '% + ' + dx + 'px))'; }
    }, {passive: true});
    vp.addEventListener('touchend', function(){
      track.classList.remove('dragging');
      if(horiz && Math.abs(dx) > 50) go(dx < 0 ? i + 1 : i - 1); else go(i);
      x0 = null; paused = false; restart();
    });
    go(0); start();
  });
})();

// ===== Параллакс фона главного блока: фон движется вдвое медленнее; на телефоне и планшете выключен =====
(function(){
  var bg = document.querySelector('.hero-bg'); if(!bg) return;
  var hero = bg.parentElement;
  var mq = window.matchMedia('(min-width: 821px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)');
  var ticking = false;
  function apply(){
    ticking = false;
    if(!mq.matches){ hero.style.removeProperty('--hero-shift'); return; }
    var r = hero.getBoundingClientRect();
    if(r.bottom < 0 || r.top > innerHeight) return;
    hero.style.setProperty('--hero-shift', (Math.max(0, -r.top) * 0.5).toFixed(1) + 'px');
  }
  window.addEventListener('scroll', function(){ if(!ticking){ ticking = true; requestAnimationFrame(apply); } }, {passive: true});
  (mq.addEventListener ? mq.addEventListener('change', apply) : mq.addListener(apply));
  apply();
})();

// ===== Плавающие шары в фоне главного экрана (цвета палитры, полупрозрачные) =====
(function(){
  var bg = document.querySelector('.hero-bg'); if(!bg || bg.querySelector('.hero-orbs')) return;
  var COL = {emerald: ['#3E8A63', '#1E4D37'], gold: ['#F0D48E', '#C79A46'], berry: ['#B24A57', '#8C2F3B'], ivory: ['#FFFFFF', '#E4D9BE']};
  // left, top (в % слоя фона), размер, цвет, прозрачность, длительность, сдвиг, задержка, только десктоп
  var ORBS = [
    [57, 40, 64, 'gold', .20, 26, '26px', '-34px', -3, 0],
    [79, 50, 112, 'emerald', .20, 34, '-30px', '-42px', -9, 0],
    [91, 37, 54, 'berry', .22, 29, '-18px', '30px', -14, 1],
    [67, 77, 88, 'berry', .16, 38, '34px', '-26px', -6, 0],
    [7, 82, 60, 'gold', .12, 31, '30px', '-28px', -18, 1],
    [44, 89, 46, 'ivory', .10, 27, '-24px', '-20px', -11, 1],
    [95, 80, 92, 'gold', .14, 36, '-36px', '-30px', -21, 0]
  ];
  var box = document.createElement('div'); box.className = 'hero-orbs'; box.setAttribute('aria-hidden', 'true');
  ORBS.forEach(function(o, i){
    var c = COL[o[3]], id = 'orbg' + i;
    var el = document.createElement('div');
    el.className = 'orb' + (o[9] ? ' o-desk' : '');
    el.style.cssText = 'left:' + o[0] + '%;top:' + o[1] + '%;--s:' + o[2] + 'px;--o:' + o[4] + ';--d:' + o[5] + 's;--dx:' + o[6] + ';--dy:' + o[7] + ';--dl:' + o[8] + 's';
    el.innerHTML = '<svg viewBox="0 0 100 124"><defs><radialGradient id="' + id + '" cx="36%" cy="34%" r="70%"><stop offset="0" stop-color="' + c[0] + '"/><stop offset="1" stop-color="' + c[1] + '"/></radialGradient></defs>' +
      '<path d="M50 0V13" stroke="#E4C77E" stroke-width="1.6"/><circle cx="50" cy="12" r="4" fill="none" stroke="#E4C77E" stroke-width="1.6"/>' +
      '<rect x="41" y="15" width="18" height="11" rx="2" fill="#C79A46"/><circle cx="50" cy="75" r="47" fill="url(#' + id + ')"/>' +
      '<ellipse cx="34" cy="56" rx="11" ry="7" fill="#fff" opacity=".35" transform="rotate(-30 34 56)"/></svg>';
    box.appendChild(el);
  });
  bg.insertBefore(box, bg.firstChild);
})();

// ===== Skeleton для фото в карточках: мерцание, пока картинка не загрузилась, затем плавное появление =====
(function(){
  var SEL = '.ws-media img, .work-btn img, .lesson-figure img, .b2b-grid img';
  function hook(img){
    if(img.dataset.skel) return; img.dataset.skel = '1';
    if(img.complete && img.naturalWidth > 0) return;
    var box = img.parentElement; box.classList.add('skel-wrap'); img.classList.add('img-wait');
    var done = function(){ img.classList.remove('img-wait'); box.classList.remove('skel-wrap'); };
    img.addEventListener('load', done, {once: true}); img.addEventListener('error', done, {once: true});
  }
  function scan(root){ (root || document).querySelectorAll(SEL).forEach(hook); }
  scan();
  var gal = document.getElementById('gallery');
  if(gal) new MutationObserver(function(){ scan(gal); }).observe(gal, {childList: true});
})();

// ===== Таймер до Нового года: дни — часы — минуты — секунды =====
(function(){
  var box = document.querySelector('[data-countdown]'); if(!box) return;
  var target = Date.parse(box.getAttribute('data-countdown'));
  var el = {}; ['d', 'h', 'm', 's'].forEach(function(k){ el[k] = box.querySelector('[data-cd="' + k + '"]'); el[k + 'l'] = box.querySelector('[data-cd-l="' + k + '"]'); });
  var FORMS = {d: ['день', 'дня', 'дней'], h: ['час', 'часа', 'часов'], m: ['минута', 'минуты', 'минут'], s: ['секунда', 'секунды', 'секунд']};
  function plural(n, f){ var a = n % 100, b = n % 10; if(a > 10 && a < 20) return f[2]; if(b === 1) return f[0]; if(b > 1 && b < 5) return f[1]; return f[2]; }
  var timer = null, prev = {};
  function tick(){
    var left = target - Date.now();
    if(left <= 0){
      clearInterval(timer); box.classList.add('is-done'); box.querySelector('.cd-done').hidden = false;
      box.setAttribute('aria-label', 'Новый год начался'); return;
    }
    var t = Math.floor(left / 1000), v = {d: Math.floor(t / 86400), h: Math.floor(t % 86400 / 3600), m: Math.floor(t % 3600 / 60), s: t % 60};
    for(var k in v){
      var txt = k === 'd' ? String(v[k]) : String(v[k]).padStart(2, '0');
      if(prev[k] !== txt){ el[k].textContent = txt; el[k].classList.remove('tick'); void el[k].offsetWidth; el[k].classList.add('tick'); prev[k] = txt; }
      el[k + 'l'].textContent = plural(v[k], FORMS[k]);
    }
    box.setAttribute('aria-label', 'До Нового года ' + v.d + ' ' + plural(v.d, FORMS.d) + ', ' + v.h + ' ' + plural(v.h, FORMS.h));
  }
  tick(); timer = setInterval(tick, 1000);
  window.SOH_countdownTest = function(ms){ target = Date.now() + ms; box.classList.remove('is-done'); box.querySelector('.cd-done').hidden = true; clearInterval(timer); tick(); timer = setInterval(tick, 1000); };
})();

// ===== Галерея фото: полноэкранный просмотр, стрелки, Esc, клик вне фото, свайп =====
(function(){
  var grids = document.querySelectorAll('[data-lightbox]'); if(!grids.length) return;
  var lb = document.createElement('div'); lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Просмотр фото');
  var ARR = function(d){ return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="' + d + '" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'; };
  lb.innerHTML = '<button class="lb-btn lb-close" type="button" aria-label="Закрыть">' + ARR('M6 6l12 12M18 6L6 18') + '</button>' +
    '<button class="lb-btn lb-prev" type="button" aria-label="Предыдущее фото">' + ARR('M15 5l-7 7 7 7') + '</button>' +
    '<figure class="lb-figure"><img alt=""><figcaption><span class="lb-count"></span><span class="lb-cap"></span></figcaption></figure>' +
    '<button class="lb-btn lb-next" type="button" aria-label="Следующее фото">' + ARR('M9 5l7 7-7 7') + '</button>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img'), cap = lb.querySelector('.lb-cap'), cnt = lb.querySelector('.lb-count');
  var items = [], i = 0, opener = null;
  function show(k){
    i = (k + items.length) % items.length; var a = items[i];
    img.classList.add('lb-swap');
    var src = a.getAttribute('href'); if(!src || src === '#') src = a.querySelector('img').src;
    var n = new Image(); n.onload = n.onerror = function(){ img.src = src; img.alt = a.querySelector('img').alt; img.classList.remove('lb-swap'); }; n.src = src;
    cap.textContent = a.getAttribute('data-caption') || ''; cnt.textContent = (i + 1) + ' / ' + items.length;
  }
  function open(list, k, from){ items = list; opener = from; show(k); lb.classList.add('open'); document.body.classList.add('lb-lock'); lb.querySelector('.lb-close').focus(); }
  function close(){ lb.classList.remove('open'); document.body.classList.remove('lb-lock'); if(opener) opener.focus(); }
  grids.forEach(function(g){
    var list = Array.prototype.slice.call(g.querySelectorAll('a.lb-item'));
    list.forEach(function(a, k){ a.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation(); open(list, k, a); }); });
  });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function(e){ e.stopPropagation(); show(i - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function(e){ e.stopPropagation(); show(i + 1); });
  lb.addEventListener('click', function(e){ if(e.target === lb || e.target.classList.contains('lb-figure')) close(); });
  document.addEventListener('keydown', function(e){
    if(!lb.classList.contains('open')) return;
    if(e.key === 'Escape') close(); else if(e.key === 'ArrowLeft') show(i - 1); else if(e.key === 'ArrowRight') show(i + 1);
    else if(e.key === 'Tab'){ var f = lb.querySelectorAll('button'); var first = f[0], last = f[f.length - 1]; if(e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); } else if(!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); } }
  });
  var x0 = null, y0 = 0;
  lb.addEventListener('touchstart', function(e){ x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, {passive: true});
  lb.addEventListener('touchend', function(e){ if(x0 === null) return; var t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0; x0 = null; if(Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(dx < 0 ? i + 1 : i - 1); });
})();

// ===== Офлайн-заглушка: service worker (только на хостинге, где есть <meta name="soh-sw">) =====
(function(){
  var m = document.querySelector('meta[name="soh-sw"]');
  if(!m || !('serviceWorker' in navigator)) return;
  if(location.protocol !== 'https:' && location.hostname !== 'localhost') return;
  window.addEventListener('load', function(){ navigator.serviceWorker.register(m.getAttribute('content')).catch(function(){}); });
})();
