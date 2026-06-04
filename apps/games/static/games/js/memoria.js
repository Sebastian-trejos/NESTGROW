/**
 * Memorama — vocabulario EN/ES con dinámicas por dificultad del juego.
 * Requiere: VOCABULARY, DIFFICULTY, GAME_ID, POINTS_REWARD, SAVE_URL, CSRF,
 * MILO_CARD_BACK_URL, CATEGORY_ICON (opcional)
 */
(function () {
  'use strict';

  const PAIRS_BY_DIFF = { 1: 4, 2: 6, 3: 8 };

  /** Palabra → emoji aproximado (heurísticas); último recurso: icono de categoría */
  const EMOJI_LEXICON = [
    [/^(apple|manzana)$/i, '🍎'], [/^(banana|plátano|platano)$/i, '🍌'], [/orange|naranja/i, '🍊'],
    [/^(grape|uva)s?$/i, '🍇'], [/^(strawberry|fresa)$/i, '🍓'], [/^(watermelon|sand[ií]a)$/i, '🍉'],
    [/bread|pan( |$)|toast/i, '🍞'], [/rice|arroz/i, '🍚'], [/egg|huevos?/i, '🥚'],
    [/cheese|queso/i, '🧀'], [/milk|leche/i, '🥛'], [/coffee|caf[eé]/i, '☕'], [/tea|t[eé]( |$)|iced tea/i, '🍵'],
    [/water|agua(?!\s*melon)/i, '💧'], [/juice|zumo|jugo/i, '🧃'], [/soda|gaseosa|refreshment/i, '🥤'],
    [/pizza/i, '🍕'], [/hamburger|burger|hamburguesa/i, '🍔'], [/sandwich|bocadillo/i, '🥪'],
    [/hot dog|perrito/i, '🌭'], [/taco/i, '🌮'], [/ice cream|helado/i, '🍨'], [/cake|past(el|él)|cupcake/i, '🎂'],
    [/cookie|galleta/i, '🍪'], [/candy|dulce|caramel/i, '🍬'], [/chocolate/i, '🍫'],
    [/salad|ensalada/i, '🥗'], [/chicken|pollo/i, '🍗'], [/fish|pez|pescado(?!\s*and)/i, '🐟'],
    [/soup|sopa/i, '🍜'], [/carrot|zanahoria/i, '🥕'], [/corn|ma[ií]z/i, '🌽'],
    [/dog$/i, '🐕'], [/cat$/i, '🐈'], [/bird|p[aá]jaro/i, '🐦'], [/fish\b/i, '🐠'],
    [/cow|vaca/i, '🐄'], [/horse|caballo/i, '🐎'], [/sheep|oveja/i, '🐑'], [/pig|cerdo/i, '🐖'],
    [/rabbit|conejo/i, '🐰'], [/frog|rana/i, '🐸'], [/bee|abeja/i, '🐝'], [/ant|hormiga/i, '🐜'],
    [/butterfly|mariposa/i, '🦋'], [/lion|le[oó]n/i, '🦁'], [/tiger|tigre/i, '🐯'],
    [/bear|oso/i, '🐻'], [/elephant|elefante/i, '🐘'], [/monkey|mono(?!\s*key\s*business)/i, '🐵'],
    [/penguin|pingüino/i, '🐧'], [/shark|tibur[oó]n/i, '🦈'],
    [/red|rojo(?!\s*social)/i, '🔴'], [/blue|azul(?!\s*pen)/i, '🔵'], [/green|verde\b/i, '🟢'],
    [/yellow|amarillo\b/i, '🟡'], [/orange(?!\s*juice|\s*$)|naranja.*color/i, '🟠'], [/purple|morado\b|violeta/i, '🟣'],
    [/black|negro(?!\s*berry)/i, '⚫'], [/white|blanco\b/i, '⚪'], [/brown|marr[oó]n|caf[eé]/i, '🟤'],
    [/pink|rosado\b|rosa\b/i, '🌸'], [/grey|gray|gris/i, '⚙️'],
    [/sun|sol(?!\s*flower)/i, '☀️'], [/moon|luna\b/i, '🌙'], [/rain|rainy|lluvia/i, '🌧️'],
    [/snow|nieve|snowy/i, '❄️'], [/storm|stormy|tormenta/i, '⛈️'],
    [/book|libro\b/i, '📚'], [/pencil|l[aá]piz/i, '✏️'], [/pen(?!\s*guin)|bol[ií]grafo/i, '🖊️'],
    [/desk| escritorio|\bpupitre/i, '📋'], [/backpack|mochila/i, '🎒'],
    [/house|casa\b/i, '🏠'], [/school|escuela|colegio/i, '🏫'], [/park|parque/i, '🏞️'],
    [/bike|bicicleta|bicycle/i, '🚲'], [/(\bcar\b|coche\b|carro\b|auto\b)/i, '🚗'],
    [/bus|autob[uú]s/i, '🚌'], [/plane|avi[oó]n/i, '✈️'], [/boat|barco\b/i, '🚤'],
    [/train|tren\b/i, '🚂'], [/bed|cama\b/i, '🛏️'], [/clock|reloj/i, '🕒'],
    [/ball|pelota\b|bal[oó]n/i, '⚽'], [/doll|muñeca/i, '🎎'], [/kite|cometa\b/i, '🪁'],
    [/gift|regalo\b/i, '🎁'], [/star\b|estrella(?!\s*wars)/i, '⭐️'], [/heart\b|coraz[oó]n/i, '❤️'],
    [/shirt|camisa\b/i, '👕'], [/pants|pantalones/i, '👖'], [/dress|vestido/i, '👗'],
    [/shoes|zapatos|zapatillas/i, '👟'], [/hat|sombrero|gorra/i, '🧢'],
    [/tree|[áa]rbol/i, '🌳'], [/flower|flores?/i, '🌼'], [/leaf|hoja\b/i, '🍃'],
    [/famil(?:y|ia)/i, '👨‍👩‍👧'], [/mother|madre|mom/i, '👩'], [/father|padre|dad/i, '👨'],
    [/sister|hermana\b/i, '👧'], [/brother|hermano\b/i, '👦'], [/baby|beb[eé]|niñ[oa]/i, '👶'],
    [/face|cara\b/i, '😊'], [/eye|ojo/i, '👀'], [/nose|nariz/i, '👃'], [/mouth|boca\b/i, '👄'],
    [/hand|mano\b/i, '✋'], [/foot|pies?|pie\b/i, '🦶'], [/hair|pelo|cabello/i, '💇'],
    [/head|cabeza/i, '🙂'], [/doctor|doctora|medico\b/i, '⚕️'], [/teacher|profes(or|ora)/i, '👩‍🏫'],
    [/sing|cantar|cante/i, '🎤'], [/dance|bail(i|ar)/i, '💃'], [/play|jugando|juego/i, '🎯'],
    [/wash|lavar|cepillo|dientes/i, '🪥'], [/brush.*hair|cepillar/i, '🖌️'],
    [/clean|limpia(?:r|ción)/i, '🧽'], [/cook|cocinar|cocina/i, '👩‍🍳'], [/read|lea|leyendo\b/i, '📖'],
    [/write|escrib(ir|iendo)/i, '✍️'], [/jump|saltar\b/i, '🤸'], [/run|corr(er|iendo)\b/i, '🏃'],
    [/swim|nad(ar|ando)/i, '🏊'], [/kick|patad/i, '🦵'], [/smile|sonr[ií]s/i, '😄'],
    [/happy|feliz|c[eé]lebre/i, '😃'], [/sad|triste\b/i, '😢'], [/angry|enfadad|furios/i, '😠'],
    [/tired|cansado\b/i, '😴'], [/scared|miedo|asusta/i, '😨'], [/cold|fr[ií]o\b/i, '🥶'],
    [/hot\b|calor\b/i, '🥵'], [/sick|enfermo\b/i, '🤒'],
    [/zero|cero\b/i, '0️⃣'],
  ];

  const DRINK_RE = /\b(juice|juices|water|soda|milk|tea|coffee|smoothie|lemonade|drink|cocoa|beer|wine|cocktail|shake|bebida|zumo|jugo|refreshment|raspberry\s+lemon)\b|\b(te|café|cafe\b|caf[eé]s|bebidas?\b)/i;
  const FOOD_RE = /\b(apple|banana|rice|bread|sandwich|pizza|hamburger|hotdog|burger|cake|cookie|pie|egg|salad|soup|meat|chicken|fish|cheese|candy|chocolate|ice\s*cream|taco|fries|toast|sandwich|cereal|oatmeal|noodle|burger|sandwich)\b|\b(fruta|comida|galletas?|sandwich\b|papas\b|huevos\b|pastel(es)?|croissant|sand[ií]a\b)\b/i;

  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function emojiForWord(word_en, word_es, categoryIcon) {
    const cand = `${word_en} ${word_es}`.trim();
    for (const row of EMOJI_LEXICON) {
      if (!row[1]) continue;
      const re = row[0];
      if (typeof re.test === 'function' && (re.test(word_en) || re.test(word_es) || re.test(cand))) {
        return row[1];
      }
    }
    return categoryIcon || '✨';
  }

  function inferDrink(blob) {
    return DRINK_RE.test(blob);
  }

  function inferFood(blob) {
    return FOOD_RE.test(blob);
  }

  function buildSubcategoryPlan(words, categoryNameEs) {
    const drinks = [];
    const foods = [];
    words.forEach((w) => {
      const blob = `${w.word_en || ''} ${w.word_es || ''}`.toLowerCase();
      const d = inferDrink(blob);
      const f = inferFood(blob);
      if (d && !f) drinks.push(w);
      else foods.push(w);
    });

    if (drinks.length >= 2 && foods.length >= 2) {
      return {
        tierAIdSet: new Set(foods.map((w) => w.id)),
        tierBIdSet: new Set(drinks.map((w) => w.id)),
        message: 'Primero encuentra todas las comidas 🍕, ¡después las bebidas! 🥤',
        labelNow: ['Comidas 🍕', 'Bebidas 🥤'],
      };
    }

    const hasDifficulty = words.some((w) => typeof w.item_difficulty === 'number');
    if (hasDifficulty) {
      const low = [];
      const high = [];
      words.forEach((w) => {
        if ((w.item_difficulty ?? 1) <= 1) low.push(w);
        else high.push(w);
      });
      if (low.length >= 2 && high.length >= 2) {
        return {
          tierAIdSet: new Set(low.map((w) => w.id)),
          tierBIdSet: new Set(high.map((w) => w.id)),
          message: `Primero palabras nivel ⭐ (${low.length}), luego ⭐⭐ (${high.length}).`,
          labelNow: [`Nivel fácil ⭐`, `Siguientes ⭐⭐`],
        };
      }
    }

    const sorted = [...words].sort((a, b) => (a.orden || 0) - (b.orden || 0));
    const mid = Math.ceil(sorted.length / 2);
    const grp1 = sorted.slice(0, mid);
    const grp2 = sorted.slice(mid);
    return {
      tierAIdSet: new Set(grp1.map((w) => w.id)),
      tierBIdSet: new Set(grp2.map((w) => w.id)),
      message: 'Primero el Grupo 🅰️ — después el 🅱️.',
      labelNow: ['Grupo 🅰️', 'Grupo 🅱️'],
    };
  }

  function tierForWordId(plan, wordId) {
    if (!plan) return 1;
    if (plan.tierAIdSet.has(wordId)) return 1;
    if (plan.tierBIdSet.has(wordId)) return 2;
    return 1;
  }

  /** Animación completa de revuelta (fácil): fly-in FLIP */
  function animateShuffle(grid) {
    return new Promise((resolve) => {
      const movable = [...grid.querySelectorAll('.memory-slot:not(.slot-matched)')];
      if (movable.length < 2 || grid.dataset.freezeShuffle === '1') {
        resolve();
        return;
      }

      let order = shuffle([...movable]);
      if (
        order.every((el, i) => el === movable[i]) &&
        movable.length >= 2
      ) {
        const ia = Math.floor(Math.random() * order.length);
        let ib = Math.floor(Math.random() * order.length);
        for (let g = 0; g < 24 && ia === ib; g++) ib = Math.floor(Math.random() * order.length);
        if (ia !== ib) [order[ia], order[ib]] = [order[ib], order[ia]];
      }

      const firstRects = new Map(movable.map((el) => [el, el.getBoundingClientRect()]));

      movable.forEach((el) => el.classList.add('memory-slot--shuffling'));
      order.forEach((slot) => grid.appendChild(slot));

      movable.forEach((slot) => {
        const r0 = firstRects.get(slot);
        const r1 = slot.getBoundingClientRect();
        const dx = r0.left - r1.left;
        const dy = r0.top - r1.top;
        slot.style.willChange = 'transform';
        slot.style.transition = 'none';
        slot.style.transform = `translate(${dx}px, ${dy}px) scale(1.06)`;
        slot.style.zIndex = '42';
      });

      const shell = grid.closest('.mem-board-shell');
      shell?.classList.add('mem-shell--shuffle-pulse');

      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          movable.forEach((slot) => {
            slot.style.transition =
              'transform 0.95s cubic-bezier(0.2, 1.15, 0.35, 1)';
            slot.style.transform = 'translate(0px, 0px) scale(1)';
          });
          setTimeout(() => {
            shell?.classList.remove('mem-shell--shuffle-pulse');
            movable.forEach((slot) => {
              slot.style.transition = '';
              slot.style.transform = '';
              slot.style.zIndex = '';
              slot.style.willChange = '';
              slot.classList.remove('memory-slot--shuffling');
            });
            resolve();
          }, 1000);
        });
      });
    });
  }

  /**
   * Animación parcial de revuelta (medio/difícil): fade-out → cambio de orden CSS → fade-in.
   * Usa la propiedad CSS `order` para reordenar visualmente sin mover el DOM,
   * evitando que las cartas ya emparejadas/desaparecidas reinicien sus animaciones.
   * Revuelve la mitad de los pares; ninguna carta puede ir a la posición de su par.
   */
  function animatePartialShuffle(grid, pairGoal) {
    return new Promise((resolve) => {
      const allSlots = [...grid.children];

      // Obtener el valor CSS order actual de un slot
      const getOrder = (slot) => parseInt(slot.style.order ?? '0') || 0;

      // Agrupar slots no emparejados por pairId
      const pairMap = new Map();
      allSlots.forEach((slot) => {
        if (slot.classList.contains('slot-matched')) return;
        const card = slot.querySelector('.memory-card');
        if (!card) return;
        const pid = card.dataset.pairId;
        if (!pairMap.has(pid)) pairMap.set(pid, []);
        pairMap.get(pid).push(slot);
      });

      // Solo pares completos (ambas cartas disponibles)
      const completePairs = [...pairMap.values()].filter((p) => p.length === 2);
      if (completePairs.length < 2) { resolve(); return; }

      const numToShuffle = Math.max(1, Math.ceil(pairGoal / 2));
      const chosenPairs = shuffle(completePairs).slice(0, Math.min(numToShuffle, completePairs.length));

      const selectedSlots = chosenPairs.flatMap((p) => p);

      // Valores CSS order actuales de cada slot seleccionado
      const selectedOrders = selectedSlots.map(getOrder);

      // Mapa de posición prohibida: un slot no puede tomar el order de su par
      const forbiddenMap = new Map();
      chosenPairs.forEach(([a, b]) => {
        forbiddenMap.set(a, getOrder(b));
        forbiddenMap.set(b, getOrder(a));
      });

      const n = selectedSlots.length;
      let perm = shuffle([...Array(n).keys()]);

      function fixViolations() {
        for (let attempt = 0; attempt < 40; attempt++) {
          const vIdx = perm.findIndex(
            (pi, i) => selectedOrders[pi] === forbiddenMap.get(selectedSlots[i])
          );
          if (vIdx === -1) break;
          let fixed = false;
          for (let j = 0; j < n; j++) {
            if (j === vIdx) continue;
            if (
              selectedOrders[perm[j]] !== forbiddenMap.get(selectedSlots[vIdx]) &&
              selectedOrders[perm[vIdx]] !== forbiddenMap.get(selectedSlots[j])
            ) {
              [perm[vIdx], perm[j]] = [perm[j], perm[vIdx]];
              fixed = true;
              break;
            }
          }
          if (!fixed) break;
        }
      }

      fixViolations();

      // Garantizar que al menos algo se mueva
      if (perm.every((v, i) => v === i) && n >= 2) {
        [perm[0], perm[1]] = [perm[1], perm[0]];
        fixViolations();
      }

      // Fade out de las cartas seleccionadas
      selectedSlots.forEach((slot) => {
        slot.style.transition = 'opacity 0.32s ease';
        slot.style.opacity = '0';
      });

      setTimeout(() => {
        // Reordenar visualmente cambiando CSS order — sin mover el DOM
        selectedSlots.forEach((slot, i) => {
          slot.style.order = selectedOrders[perm[i]];
        });

        // Fade in
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            selectedSlots.forEach((slot) => {
              slot.style.transition = 'opacity 0.38s ease';
              slot.style.opacity = '1';
            });
            setTimeout(() => {
              selectedSlots.forEach((slot) => {
                slot.style.transition = '';
                slot.style.opacity = '';
              });
              resolve();
            }, 420);
          });
        });
      }, 370);
    });
  }

  function initMemoria(opts) {
    const {
      VOCABULARY,
      DIFFICULTY,
      GAME_ID,
      POINTS_REWARD,
      PENALTY_AMOUNT = 2,
      SAVE_URL,
      CSRF,
      MILO_CARD_BACK_URL,
      CATEGORY_ICON = '✨',
      CATEGORY_NAME_ES = '',
      categoryColor = '#6C63FF',
      autoStartPlay = false,
    } = opts;

    let ptsPerAction = POINTS_REWARD;
    let flipped = [],
      matched = 0,
      score = 0,
      matchedPairIndices = new Set(),
      phase = 1,
      startTime,
      timerInterval,
      timeSpent = 0;
    let canFlip = true;
    let shuffleTimer = null;       // setInterval para modo fácil
    let shuffleTickTimer = null;   // setTimeout para modo medio/difícil
    let shuffleCount = 0;          // contador de revueltas (para corte de luz en difícil)
    let wrongStreak = 0;           // errores consecutivos (penalidad cada 3)
    let lightsOutActive = false;
    let blackoutTimer = null;
    let subPlan = null;
    let activeWords = [];

    const pairGoal = PAIRS_BY_DIFF[DIFFICULTY] || 6;
    const shuffleEveryMs = 15000; // modo fácil
    const usePhaseOrder = false; // mecánica de subcategorías eliminada
    const useBlackout = DIFFICULTY === 3;

    const bannerEl = document.getElementById('memBannerText');
    const phaseEl = document.getElementById('memPhaseHint');
    const msgToast = document.getElementById('memToast');

    function showToast(txt) {
      if (!msgToast) return;
      msgToast.textContent = txt;
      msgToast.style.opacity = '1';
      msgToast.style.transform = 'translateX(-50%) translateY(0)';
      clearTimeout(showToast._t);
      showToast._t = setTimeout(() => {
        msgToast.style.opacity = '0';
        msgToast.style.transform = 'translateX(-50%) translateY(10px)';
      }, 2600);
    }

    function updatePhaseBanner() {
      if (!usePhaseOrder || !subPlan) return;
      if (phaseEl) phaseEl.innerHTML =
        `<span class="mem-phase-chip">¡Fase ${phase}!</span> ` +
        (phase === 1
          ? `Encuentra: <strong>${subPlan.labelNow[0]}</strong>`
          : `¡Ahora! <strong>${subPlan.labelNow[1]}</strong>`);
    }

    function tier1PairIndices() {
      return new Set(activeWords.reduce((acc, w, idx) => {
        if (tierForWordId(subPlan, w.id) === 1) acc.push(idx);
        return acc;
      }, []));
    }

    function tryAdvancePhase(pairIndex) {
      if (!usePhaseOrder || !subPlan || phase !== 1) return;
      const w = activeWords[pairIndex];
      if (!w || tierForWordId(subPlan, w.id) !== 1) return;
      const need = tier1PairIndices();
      let ok = true;
      need.forEach((idx) => {
        if (!matchedPairIndices.has(idx)) ok = false;
      });
      if (need.size === 0) return;
      if (ok) {
        phase = 2;
        showToast(`¡Genial! Ahora: ${subPlan.labelNow[1]}`);
        updatePhaseBanner();
      }
    }

    function buildCard(word, pairIndex, type) {
      const text = type === 'en' ? word.word_en : word.word_es;
      // Visual: imagen estática/subida → emoji heurístico → icono de categoría
      const visualHtml = word.image
        ? `<img src="${word.image}" alt="${word.word_en}" class="memory-img">`
        : `<span class="memory-emoji">${emojiForWord(word.word_en, word.word_es, CATEGORY_ICON)}</span>`;
      const wrap = document.createElement('div');
      wrap.className = 'memory-slot';
      wrap.innerHTML =
        `<div class="memory-card" data-pair-id="${pairIndex}" data-type="${type}"
             data-tier="${tierForWordId(subPlan, word.id)}">` +
        '<div class="memory-inner">' +
        `<div class="memory-face memory-cover" aria-hidden="true">` +
        `<span class="mem-cover-pattern"></span>` +
        `<img class="memory-milo-thumb" src="${MILO_CARD_BACK_URL}" alt="" width="64" height="64" draggable="false">` +
        '</div>' +
        `<div class="memory-face memory-reveal">` +
        visualHtml +
        `<span class="memory-lang">${text}</span>` +
        '</div></div></div>';
      wrap.querySelector('.memory-card').addEventListener('click', () => {
        flipCard(wrap.querySelector('.memory-card'));
      });
      return wrap;
    }

    function freezeShuffle(ms) {
      const grid = document.getElementById('memoryGrid');
      if (!grid) return;
      grid.dataset.freezeShuffle = '1';
      setTimeout(() => { grid.dataset.freezeShuffle = '0'; }, ms);
    }

    /** Revuelta completa en intervalos fijos — solo modo fácil */
    function scheduleShuffle() {
      clearInterval(shuffleTimer);
      shuffleTimer = setInterval(async () => {
        const grid = document.getElementById('memoryGrid');
        if (!grid || lightsOutActive || flipped.length || !canFlip) return;
        freezeShuffle(1150);
        await animateShuffle(grid);
      }, shuffleEveryMs);
    }

    /** Revuelta parcial probabilística — modo medio y difícil.
     *  Espera 20 s, luego cada segundo tiene 1/4 de probabilidad de revolver. */
    function scheduleRandomShuffle() {
      clearTimeout(shuffleTickTimer);
      shuffleTickTimer = setTimeout(() => {
        function tick() {
          clearTimeout(shuffleTickTimer);
          shuffleTickTimer = setTimeout(async () => {
            const grid = document.getElementById('memoryGrid');
            if (
              !grid ||
              grid.dataset.freezeShuffle === '1' ||
              lightsOutActive ||
              flipped.length ||
              !canFlip
            ) {
              tick();
              return;
            }
            if (Math.random() < 0.25) {
              // Corte de luz en difícil: se activa ANTES de la revuelta (misma llamada de evento)
              if (useBlackout && (shuffleCount + 1) % 3 === 0) {
                triggerBlackoutOnce();
              }
              grid.dataset.freezeShuffle = '1';
              await animatePartialShuffle(grid, pairGoal);
              grid.dataset.freezeShuffle = '0';
              shuffleCount++;
              // Cooldown: esperar 20 s antes de que pueda volver a ocurrir una revuelta
              clearTimeout(shuffleTickTimer);
              shuffleTickTimer = setTimeout(() => tick(), 20000);
            } else {
              tick();
            }
          }, 1000);
        }
        tick();
      }, 20000);
    }

    /** Corte de luz puntual (hard mode), desencadenado por conteo de revueltas */
    function triggerBlackoutOnce() {
      const ov = document.getElementById('memBlackout');
      if (!ov || lightsOutActive) return;
      lightsOutActive = true;
      document.querySelectorAll('.memory-card.flipped:not(.matched)').forEach((card) => {
        const inn = card.querySelector('.memory-inner');
        if (inn) inn.classList.remove('flipped');
        card.classList.remove('flipped');
      });
      flipped = [];
      canFlip = false;
      ov.classList.add('mem-blackout--on');
      ov.setAttribute('aria-hidden', 'false');
      setTimeout(() => {
        ov.classList.remove('mem-blackout--on');
        ov.setAttribute('aria-hidden', 'true');
        lightsOutActive = false;
        canFlip = true;
      }, 2500);
    }

    function init() {
      const pool = shuffle(VOCABULARY.filter((v) => v.word_en && v.word_es));
      if (pool.length < pairGoal) {
        showToast('¡Necesitamos más palabras en esta categoría!');
      }
      activeWords = pool.slice(0, Math.min(pairGoal, pool.length));
      const totalPairs = activeWords.length;
      ptsPerAction = Math.max(1, Math.round(POINTS_REWARD / totalPairs));
      document.getElementById('totalPairs').textContent = totalPairs;

      subPlan = buildSubcategoryPlan(activeWords, CATEGORY_NAME_ES);
      if (usePhaseOrder && bannerEl) {
        bannerEl.innerHTML = `${subPlan.message}`;
      } else if (bannerEl) {
        bannerEl.textContent = '¡Encuentra todas las parejas! Voltea las tarjetas y memoriza.';
      }
      updatePhaseBanner();

      const cards = shuffle([
        ...activeWords.map((w, i) => ({ w, i, type: 'en' })),
        ...activeWords.map((w, i) => ({ w, i, type: 'es' })),
      ]);

      const grid = document.getElementById('memoryGrid');
      grid.innerHTML = '';
      grid.style.setProperty('--mem-accent', categoryColor);
      grid.dataset.cardCount = String(cards.length);
      grid.classList.remove(
        'memory-grid--pairs4',
        'memory-grid--pairs6',
        'memory-grid--pairs8',
      );
      const pc = cards.length === 16 ? 'pairs8' : cards.length === 12 ? 'pairs6' : 'pairs4';
      grid.classList.add(`memory-grid--${pc}`);
      cards.forEach((c, idx) => {
        const slot = buildCard(c.w, c.i, c.type);
        slot.style.order = idx; // necesario para animatePartialShuffle con CSS order
        grid.appendChild(slot);
      });

      // Programar revueltas según dificultad
      if (DIFFICULTY === 1) {
        scheduleShuffle();
      } else {
        scheduleRandomShuffle();
      }

      startTime = Date.now();
      timerInterval = setInterval(() => {
        timeSpent = Math.floor((Date.now() - startTime) / 1000);
        const m = String(Math.floor(timeSpent / 60)).padStart(2, '0');
        const s = String(timeSpent % 60).padStart(2, '0');
        const el = document.getElementById('timerDisplay');
        if (el) el.textContent = `${m}:${s}`;
      }, 1000);
    }

    /**
     * Penalización cada 3 errores consecutivos.
     * Los errores se resetean al encontrar un par correcto.
     */
    function handleWrongPair() {
      wrongStreak++;
      if (wrongStreak >= 3) {
        wrongStreak = 0;
        score = Math.max(0, score - PENALTY_AMOUNT);
        const sd = document.getElementById('scoreDisplay');
        if (sd) sd.textContent = score;
        showToast(`¡3 errores seguidos! -${PENALTY_AMOUNT} pts`);
        showScoreToast(PENALTY_AMOUNT, false);
      } else {
        showToast(`¡Casi! ${wrongStreak}/3 errores — ¡sigue intentando!`);
      }
    }

    function pairAllowedForPhase(pairId) {
      if (!usePhaseOrder || !subPlan) return true;
      const w = activeWords[+pairId];
      if (!w) return true;
      const t = tierForWordId(subPlan, w.id);
      if (phase === 1) return t === 1;
      return t === 2;
    }

    function flipCard(el) {
      if (lightsOutActive) return;
      if (!canFlip || el.classList.contains('matched') || el.classList.contains('flipped')) return;
      const inner = el.querySelector('.memory-inner');
      if (!pairAllowedForPhase(el.dataset.pairId)) {
        el.classList.add('memory-wrong-tier');
        showToast(phase === 1
          ? `¡Primero termina: ${subPlan.labelNow[0]}!`
          : '¡Sigue con las del segundo grupo!');
        setTimeout(() => el.classList.remove('memory-wrong-tier'), 650);
        return;
      }
      inner.classList.add('flipped');
      el.classList.add('flipped');
      flipped.push(el);
      if (flipped.length === 2) {
        canFlip = false;
        const [a, b] = flipped;
        const samePair = a.dataset.pairId === b.dataset.pairId && a.dataset.type !== b.dataset.type;
        const tierOk = pairAllowedForPhase(a.dataset.pairId) && pairAllowedForPhase(b.dataset.pairId);

        if (samePair && tierOk) {
          a.classList.add('matched');
          b.classList.add('matched');
          // Overlay verde + chulito, luego desaparece
          a.classList.add('matched-success');
          b.classList.add('matched-success');
          setTimeout(() => {
            a.closest('.memory-slot')?.classList.add('slot-vanish');
            b.closest('.memory-slot')?.classList.add('slot-vanish');
          }, 750);
          a.closest('.memory-slot')?.classList.add('slot-matched');
          b.closest('.memory-slot')?.classList.add('slot-matched');
          matched++;
          score += ptsPerAction;
          wrongStreak = 0; // resetear errores consecutivos al acertar
          matchedPairIndices.add(Number(a.dataset.pairId));
          document.getElementById('matchCount').textContent = matched;
          document.getElementById('scoreDisplay').textContent = score;
          showScoreToast(ptsPerAction, true);
          flipped = [];
          canFlip = true;
          tryAdvancePhase(Number(a.dataset.pairId));
          const totalPairs = parseInt(document.getElementById('totalPairs').textContent, 10);
          if (matched === totalPairs) endGame();
        } else {
          handleWrongPair();
          setTimeout(() => {
            [a, b].forEach((x) => {
              const inn = x.querySelector('.memory-inner');
              inn.classList.remove('flipped');
              x.classList.remove('flipped');
            });
            flipped = [];
            canFlip = true;
          }, 950);
        }
      }
    }

    async function endGame() {
      clearInterval(timerInterval);
      clearInterval(shuffleTimer);
      clearTimeout(shuffleTickTimer);
      clearTimeout(blackoutTimer);
      lightsOutActive = false;
      const bob = document.getElementById('memBlackout');
      if (bob) {
        bob.classList.remove('mem-blackout--on');
        bob.setAttribute('aria-hidden', 'true');
      }
      const totalPairs = parseInt(document.getElementById('totalPairs').textContent, 10);
      const _rawMax = totalPairs * ptsPerAction;
      const _finalScore = _rawMax > 0 ? Math.round((score / _rawMax) * POINTS_REWARD) : 0;
      const maxScore = POINTS_REWARD;
      const pct = maxScore > 0 ? Math.round((_finalScore / maxScore) * 100) : 0;
      document.getElementById('winScore').textContent = _finalScore;
      document.getElementById('winTime').textContent = timeSpent;
      const $ = id => document.getElementById(id);
      let tier, stars, miloFile, msg;
      if (pct >= 90)      { tier='excelente'; stars='⭐⭐⭐'; miloFile='milo_fest.png'; msg='¡Memoria de elefante!'; }
      else if (pct >= 60) { tier='bien';      stars='⭐⭐';   miloFile='milo_saludando.png'; msg='¡Bien hecho!'; }
      else                { tier='regular';   stars='⭐';    miloFile='milo_lupa1.png'; msg='¡Sigue practicando!'; }
      if ($('winMilo')) $('winMilo').src = (window.STATIC_URL || '/static/') + 'img/' + miloFile;
      if ($('winMessage')) $('winMessage').textContent = msg;
      if ($('winStars')) $('winStars').textContent = stars;
      const card = document.querySelector('#winOverlay .win-card');
      if (card) { card.className = 'win-card'; card.classList.add('win-card--' + tier); }
      if ((tier==='excelente'||tier==='bien') && typeof launchConfetti==='function') launchConfetti();
      $('winOverlay').style.display = 'flex';
      try {
        const res = await fetch(SAVE_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
          body: JSON.stringify({
            game_id: GAME_ID,
            score: _finalScore,
            max_score: maxScore,
            time_spent: timeSpent,
            completed: true,
          }),
        });
        const data = await res.json();
        if (data.registro_pk && $('btnVolverPanel')) {
          $('btnVolverPanel').href =
            '/talleres/mis-talleres/?revisado=' + data.registro_pk;
        }
      } catch (e) { /* silencio */ }
    }

    const startBtn = document.getElementById('startGameBtn');
    if (autoStartPlay) {
      const gs = document.getElementById('gameSection');
      if (gs) gs.style.display = 'block';
      init();
    } else if (startBtn) {
      startBtn.addEventListener(
        'click',
        () => { init(); },
        { once: true },
      );
    } else {
      const gs = document.getElementById('gameSection');
      if (gs) gs.style.display = 'block';
      init();
    }
  }

  window.initMemoria = initMemoria;
})();
