// ============================================================
// NESTGROW — Conectar imágenes con palabras
// ============================================================

const DIFFICULTY_CONFIG = {
  1: {
    pairCount:         8,
    layout:           'sorted',   // sin cruces de cables
    emojiSize:        '2.8rem',
    memoryFlip:        false,
    memoryFlipCount:   0,
    memoryRevealMs:    0,
    comboSystem:       false,
    comboThreshold:    3,
    timeBonusPerCombo: 0,
    penalizeWrong:     false,
    wrongPenaltyPts:   0,
    feedbackDelay:     380,
    instruction: '¡Haz clic en un emoji y luego en su palabra para conectarlos!',
  },
  2: {
    pairCount:         12,
    layout:           'shuffled', // posiciones aleatorias → cruces naturales de cables
    emojiSize:        '2.3rem',
    memoryFlip:        false,
    memoryFlipCount:   0,
    memoryRevealMs:    0,
    comboSystem:       true,
    comboThreshold:    3,
    timeBonusPerCombo: 0,
    penalizeWrong:     false,
    wrongPenaltyPts:   0,
    feedbackDelay:     200,
    instruction: '¡Conecta cada emoji con su palabra! Ojo con las palabras parecidas.',
  },
  3: {
    pairCount:         16,
    layout:           'shuffled',
    emojiSize:        '2rem',
    memoryFlip:        true,
    memoryFlipCount:   4,
    memoryRevealMs:    4000,
    comboSystem:       true,
    comboThreshold:    3,
    timeBonusPerCombo: 8,
    penalizeWrong:     true,
    wrongPenaltyPts:   5,
    feedbackDelay:     80,
    instruction: '¡Memoriza los emojis, conecta rápido y no te equivoques!',
  },
};

// Paleta de 16 colores distintos para los cables
const CABLE_COLORS = [
  '#6C63FF','#FF6B6B','#27ae60','#e67e22','#2980b9',
  '#8e44ad','#16a085','#c0392b','#f39c12','#1abc9c',
  '#e91e63','#3f51b5','#4caf50','#ff5722','#795548','#607d8b',
];

function initConnectGame(vocabulary, gameId, timeLimit, pointsReward, penaltyAmount, difficulty) {
  const cfg = DIFFICULTY_CONFIG[difficulty] || DIFFICULTY_CONFIG[1];

  // ── Preparar ítems ──────────────────────────────────────
  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  let pool = [...vocabulary];
  if (pool.length === 0) {
    const gs = document.getElementById('gameSection');
    if (gs) {
      gs.innerHTML = `<div class="alert text-center p-5 rounded-4" style="background:#fff9ee;border:2px solid #FFB347">
        <div style="font-size:3rem">⚠️</div>
        <h5 class="fw-bold mt-2" style="color:#8B4513">Esta categoría no tiene vocabulario</h5>
        <p class="mb-0" style="color:#8B4513">El profesor debe agregar palabras a la categoría antes de jugar.</p>
      </div>`;
      gs.style.display = 'block';
    }
    return;
  }
  // Si el vocabulario tiene menos ítems que los pares requeridos, repetir
  while (pool.length < cfg.pairCount) pool = [...pool, ...vocabulary];

  const items = cfg.layout === 'sorted'
    ? pool.slice(0, cfg.pairCount)
    : shuffle(pool).slice(0, cfg.pairCount);

  if (items.length === 0) {
    // Mostrar aviso amigable si no hay vocabulario
    const gs = document.getElementById('gameSection');
    if (gs) {
      gs.innerHTML = `<div class="alert text-center p-5 rounded-4" style="background:#fff9ee;border:2px solid #FFB347">
        <div style="font-size:3rem">⚠️</div>
        <h5 class="fw-bold mt-2" style="color:#8B4513">Esta categoría no tiene vocabulario</h5>
        <p class="mb-0" style="color:#8B4513">El profesor debe agregar palabras a la categoría antes de jugar.</p>
      </div>`;
      gs.style.display = 'block';
    }
    return;
  }

  const ptsPerPair  = Math.max(1, Math.round(pointsReward / items.length));
  const maxScoreVal = items.length * ptsPerPair;

  // ── Estado ──────────────────────────────────────────────
  // connections: Map<emojiId, wordId>   — emoji conectado a qué palabra
  // wordToEmoji: Map<wordId, emojiId>   — inverso para búsqueda rápida
  // lines: Map<emojiId, SVGLineElement>
  const connections = new Map();
  const wordToEmoji = new Map();
  const lines       = new Map();
  let selectedNode  = null; // { type: 'emoji'|'word', id, el }
  let comboStreak   = 0;
  let score         = 0;
  let checked       = false;
  let timer         = null;
  const hiddenEmojis = new Set();

  // ── DOM refs ─────────────────────────────────────────────
  const emojiCol      = document.getElementById('emojiNodes');
  const wordCol       = document.getElementById('wordNodes');
  const svg           = document.getElementById('connectSvg');
  const gameArea      = document.getElementById('connectGame');
  const checkBtn      = document.getElementById('checkBtn');
  const scoreDisp     = document.getElementById('scoreDisplay');
  const maxScoreEl    = document.getElementById('maxScore');
  const comboBadge    = document.getElementById('comboBadge');
  const comboCountEl  = document.getElementById('comboCount');
  const miloInstr     = document.getElementById('miloInstruction');
  const memCdEl       = document.getElementById('memoryCountdown');
  const cdSecsEl      = document.getElementById('countdownSecs');

  maxScoreEl.textContent  = maxScoreVal;
  if (miloInstr) miloInstr.textContent = cfg.instruction;

  // ── Render emoji visual ──────────────────────────────────
  function renderEmojiVisual(item) {
    if (item.emoji) {
      return `<span class="connect-emoji-glyph" style="font-size:${cfg.emojiSize}">${item.emoji}</span>`;
    }
    if (item.image) {
      return `<img src="${item.image}" alt="${item.word_en}"
               style="width:56px;height:56px;object-fit:cover;border-radius:12px;display:block">`;
    }
    return `<div class="connect-emoji-fallback">${item.word_en[0].toUpperCase()}</div>`;
  }

  // ── Construir nodos emoji (columna izquierda) ─────────────
  items.forEach(item => {
    const id   = String(item.id);
    const node = document.createElement('div');
    node.className     = 'connect-node connect-node--emoji mb-2';
    node.dataset.id    = id;
    node.dataset.answer = item.word_en;

    node.innerHTML = `
      <div class="connect-emoji-wrap">
        <div class="connect-emoji-front">${renderEmojiVisual(item)}</div>
        <div class="connect-emoji-back">❓</div>
      </div>
      <div class="connect-node-label">${item.word_es}</div>`;

    node.addEventListener('click', () => onNodeClick('emoji', id, node));
    emojiCol.appendChild(node);
  });

  // ── Construir nodos palabra (columna derecha, siempre mezcladas) ──
  shuffle(items).forEach(item => {
    const id   = String(item.id);
    const node = document.createElement('div');
    node.className    = 'connect-node connect-node--word mb-2';
    node.dataset.id   = id;
    node.dataset.word = item.word_en;
    node.textContent  = item.word_en;
    node.addEventListener('click', () => onNodeClick('word', id, node));
    wordCol.appendChild(node);
  });

  // ── Modo Memoria (difícil) ───────────────────────────────
  if (cfg.memoryFlip && cfg.memoryFlipCount > 0) {
    const allIds = items.map(it => String(it.id));
    shuffle(allIds).slice(0, cfg.memoryFlipCount).forEach(id => hiddenEmojis.add(id));

    if (memCdEl) {
      memCdEl.style.display = 'block';
      let secsLeft = Math.ceil(cfg.memoryRevealMs / 1000);
      if (cdSecsEl) cdSecsEl.textContent = secsLeft;

      const cdInterval = setInterval(() => {
        secsLeft--;
        if (cdSecsEl) cdSecsEl.textContent = Math.max(0, secsLeft);
        if (secsLeft <= 0) {
          clearInterval(cdInterval);
          if (memCdEl) memCdEl.style.display = 'none';
          hiddenEmojis.forEach(id => {
            const node = emojiCol.querySelector(`[data-id="${id}"]`);
            if (node) node.classList.add('connect-node--hidden');
          });
        }
      }, 1000);
    }
  }

  // ── Interacción: click en nodo ───────────────────────────
  function onNodeClick(type, id, el) {
    if (checked) return;

    if (!selectedNode) {
      select(type, id, el);
      return;
    }

    if (selectedNode.type === type) {
      // Misma columna: cambiar selección
      if (selectedNode.id === id) {
        clearSelection();
      } else {
        clearSelection();
        select(type, id, el);
      }
      return;
    }

    // Columnas diferentes → conectar
    const emojiId = type === 'emoji' ? id : selectedNode.id;
    const wordId  = type === 'word'  ? id : selectedNode.id;
    clearSelection();
    connectNodes(emojiId, wordId);
  }

  function select(type, id, el) {
    selectedNode = { type, id, el };
    el.classList.add('connect-node--selected');
  }

  function clearSelection() {
    if (selectedNode) {
      selectedNode.el.classList.remove('connect-node--selected');
      selectedNode = null;
    }
  }

  // ── Conectar par ─────────────────────────────────────────
  function connectNodes(emojiId, wordId) {
    // Liberar conexión anterior del emoji
    if (connections.has(emojiId)) {
      const prevWordId = connections.get(emojiId);
      wordToEmoji.delete(prevWordId);
      removeLine(emojiId);
      const prevWordNode = wordCol.querySelector(`[data-id="${prevWordId}"]`);
      if (prevWordNode) prevWordNode.classList.remove('connect-node--connected');
    }

    // Liberar conexión anterior de la palabra
    if (wordToEmoji.has(wordId)) {
      const prevEmojiId = wordToEmoji.get(wordId);
      connections.delete(prevEmojiId);
      removeLine(prevEmojiId);
      const prevEmojiNode = emojiCol.querySelector(`[data-id="${prevEmojiId}"]`);
      if (prevEmojiNode) prevEmojiNode.classList.remove('connect-node--connected');
    }

    // Crear nueva conexión
    connections.set(emojiId, wordId);
    wordToEmoji.set(wordId, emojiId);
    drawLine(emojiId, wordId);

    const emojiNode = emojiCol.querySelector(`[data-id="${emojiId}"]`);
    const wordNode  = wordCol.querySelector(`[data-id="${wordId}"]`);
    if (emojiNode) emojiNode.classList.add('connect-node--connected');
    if (wordNode)  wordNode.classList.add('connect-node--connected');

    checkAllConnected();
  }

  // ── SVG Cables ───────────────────────────────────────────
  function getCenter(el) {
    const er = el.getBoundingClientRect();
    const cr = gameArea.getBoundingClientRect();
    return {
      x: er.left - cr.left + er.width  / 2,
      y: er.top  - cr.top  + er.height / 2,
    };
  }

  function drawLine(emojiId, wordId) {
    const emojiNode = emojiCol.querySelector(`[data-id="${emojiId}"]`);
    const wordNode  = wordCol.querySelector(`[data-id="${wordId}"]`);
    if (!emojiNode || !wordNode) return;

    const p1    = getCenter(emojiNode);
    const p2    = getCenter(wordNode);
    const idx   = items.findIndex(it => String(it.id) === emojiId);
    const color = CABLE_COLORS[idx % CABLE_COLORS.length];

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', p1.x);
    line.setAttribute('y1', p1.y);
    line.setAttribute('x2', p2.x);
    line.setAttribute('y2', p2.y);
    line.setAttribute('stroke', color);
    line.setAttribute('stroke-width', '3.5');
    line.setAttribute('stroke-linecap', 'round');
    line.setAttribute('opacity', '0.82');
    line.classList.add('connect-cable');
    svg.appendChild(line);
    lines.set(emojiId, line);
  }

  function removeLine(emojiId) {
    const line = lines.get(emojiId);
    if (line) { svg.removeChild(line); lines.delete(emojiId); }
  }

  function redrawAllLines() {
    connections.forEach((wordId, emojiId) => { removeLine(emojiId); drawLine(emojiId, wordId); });
  }

  window.addEventListener('resize', redrawAllLines);

  // ── Verificar si todo está conectado ─────────────────────
  function checkAllConnected() {
    if (connections.size === items.length) {
      checkBtn.style.display = 'inline-block';
      checkBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      checkBtn.style.display = 'none';
    }
  }

  // ── Verificación final ───────────────────────────────────
  checkBtn.addEventListener('click', () => {
    if (checked) return;
    checked = true;
    clearSelection();
    if (timer) timer.stop();

    let rawScore    = 0;
    let streak      = 0;
    let totalCombos = 0;
    let delay       = 0;
    const elapsed   = timer ? timer.getElapsed() : 0;
    window.timeSpent = elapsed;

    const emojiNodeEls = emojiCol.querySelectorAll('.connect-node--emoji');

    emojiNodeEls.forEach(emojiEl => {
      const emojiId  = String(emojiEl.dataset.id);
      const wordId   = connections.get(emojiId);
      // Correcto si el ID de la palabra conectada coincide con el ID del emoji
      const isCorrect = wordId !== undefined && wordId === emojiId;
      const wordNode  = wordId ? wordCol.querySelector(`[data-id="${wordId}"]`) : null;
      const line      = lines.get(emojiId);

      setTimeout(() => {
        if (isCorrect) {
          rawScore += ptsPerPair;
          streak++;

          emojiEl.classList.add('connect-node--correct');
          if (wordNode) wordNode.classList.add('connect-node--correct');
          if (line) {
            line.setAttribute('stroke', '#4CAF50');
            line.setAttribute('stroke-width', '5');
            line.setAttribute('opacity', '1');
          }
          // Revelar emoji oculto (modo memoria)
          if (hiddenEmojis.has(emojiId)) {
            emojiEl.classList.remove('connect-node--hidden');
            emojiEl.classList.add('connect-node--revealed');
          }
          showScoreToast(ptsPerPair, true);

          // Sistema de combos
          if (cfg.comboSystem && streak >= cfg.comboThreshold) {
            totalCombos++;
            setTimeout(() => triggerCombo(streak), 150);
            // Bonus de tiempo en difícil
            if (cfg.timeBonusPerCombo > 0 && timer && timer.addTime) {
              timer.addTime(cfg.timeBonusPerCombo);
            }
          }
        } else {
          streak = 0;
          if (cfg.penalizeWrong) rawScore -= cfg.wrongPenaltyPts;

          emojiEl.classList.add('connect-node--wrong');
          if (wordNode) wordNode.classList.add('connect-node--wrong');
          if (line) {
            line.setAttribute('stroke', '#FF6B6B');
            line.setAttribute('stroke-width', '5');
            line.setAttribute('opacity', '1');
          }
          // Revelar emoji oculto aunque sea incorrecto
          if (hiddenEmojis.has(emojiId)) emojiEl.classList.remove('connect-node--hidden');
          if (cfg.penalizeWrong) showScoreToast(cfg.wrongPenaltyPts, false);
        }

        score = Math.max(0, rawScore);
        scoreDisp.textContent = score;
      }, delay);

      delay += cfg.feedbackDelay + 160;
    });

    setTimeout(() => {
      score = Math.max(0, rawScore);
      showWinScreen(score, maxScoreVal, gameId);
    }, delay + 700);
  });

  // ── Combo toast ──────────────────────────────────────────
  function triggerCombo(streak) {
    if (!comboBadge || !comboCountEl) return;
    comboBadge.style.display = 'block';
    comboCountEl.textContent = streak;
    comboBadge.classList.remove('connect-combo-pop');
    void comboBadge.offsetWidth; // reflow para re-disparar animación
    comboBadge.classList.add('connect-combo-pop');
  }

  // ── Timer ────────────────────────────────────────────────
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => checkBtn.click());
    timer.start();
    timer.addTime = function (secs) {
      this.remaining = Math.min(this.remaining + secs, this.total * 2);
      if (timerEl) {
        timerEl.style.color = '#4CAF50';
        setTimeout(() => { if (timerEl) timerEl.style.color = ''; }, 1400);
      }
    };
  }
}
