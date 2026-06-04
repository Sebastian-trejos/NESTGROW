// ============================================================
// NESTGROW - Word Search Game
// Grid size varies by difficulty: easy=8x8, medium=12x12, hard=16x16
// Words come automatically from the game's vocabulary category
// ============================================================

function initWordSearch(vocabulary, gameId, timeLimit, pointsReward, difficulty, penaltyAmount, customWords) {
  const GRID_SIZE = difficulty === 3 ? 14 : difficulty === 2 ? 11 : 8;
  const MAX_WORDS = difficulty === 3 ? 10 : difficulty === 2 ? 7 : 5;
  const COLORS = ['#e74c3c','#3498db','#2ecc71','#9b59b6','#f39c12','#1abc9c','#e91e63','#ff5722'];

  let words;
  if (customWords && customWords.length > 0) {
    words = customWords.map(w => w.toUpperCase().replace(/\s/g, '')).filter(w => w.length >= 2 && w.length <= GRID_SIZE).slice(0, MAX_WORDS);
  } else {
    words = vocabulary.map(v => v.word_en.toUpperCase().replace(/\s/g, '')).filter(w => w.length >= 2 && w.length <= GRID_SIZE).slice(0, MAX_WORDS);
  }
  const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  let grid = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(''));
  let placedWords = [];
  const directions = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[1,-1],[-1,1]];

  words.forEach(word => {
    if (word.length > GRID_SIZE) return;
    let placed = false;
    for (let attempt = 0; attempt < 200 && !placed; attempt++) {
      const [dr, dc] = directions[Math.floor(Math.random() * directions.length)];
      const startR = Math.floor(Math.random() * GRID_SIZE);
      const startC = Math.floor(Math.random() * GRID_SIZE);
      let canPlace = true;
      const cells = [];
      for (let i = 0; i < word.length; i++) {
        const r = startR + i * dr, c = startC + i * dc;
        if (r < 0 || r >= GRID_SIZE || c < 0 || c >= GRID_SIZE) { canPlace = false; break; }
        if (grid[r][c] && grid[r][c] !== word[i]) { canPlace = false; break; }
        cells.push([r, c]);
      }
      if (canPlace) {
        cells.forEach(([r,c], i) => grid[r][c] = word[i]);
        placedWords.push({ word, cells });
        placed = true;
      }
    }
  });

  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (!grid[r][c]) grid[r][c] = ALPHABET[Math.floor(Math.random() * 26)];

  const cellSize = GRID_SIZE <= 8 ? 42 : GRID_SIZE <= 11 ? 34 : 28;
  const gridEl    = document.getElementById('wsGrid');
  const overlaysEl = document.getElementById('wsOverlays');

  gridEl.style.gridTemplateColumns = `repeat(${GRID_SIZE}, 1fr)`;

  const styleEl = document.createElement('style');
  styleEl.textContent = `.ws-cell { width:${cellSize}px !important; height:${cellSize}px !important; font-size:${cellSize <= 28 ? '0.8' : cellSize <= 34 ? '0.9' : '1.05'}rem !important; }`;
  document.head.appendChild(styleEl);

  grid.forEach((row, r) => {
    row.forEach((letter, c) => {
      const cell = document.createElement('div');
      cell.className = 'ws-cell';
      cell.textContent = letter;
      cell.dataset.r = r;
      cell.dataset.c = c;
      gridEl.appendChild(cell);
    });
  });

  const wordListEl   = document.getElementById('wordList');
  const totalWordsEl = document.getElementById('totalWords');
  const foundCountEl = document.getElementById('foundCount');
  const scoreDisplay = document.getElementById('scoreDisplay');
  totalWordsEl.textContent = placedWords.length;

  placedWords.forEach(({ word }) => {
    const chip = document.createElement('div');
    chip.className = 'ws-word-chip';
    chip.dataset.word = word;
    chip.textContent = word;
    wordListEl.appendChild(chip);
  });

  const ptsPerAction = Math.max(1, Math.round(pointsReward / placedWords.length));

  let currentMode   = 'drag';
  let selecting     = false;
  let startCell     = null;
  let selectedCells = [];
  let foundWords    = new Set();
  let colorIndex    = 0;
  let score         = 0;
  let previewPill   = null;

  // ── Pill factory ────────────────────────────────────────────

  function buildPill(cells, fill, border) {
    const wrapper = document.getElementById('wsGridWrapper');
    const wRect = wrapper.getBoundingClientRect();
    const fRect = cells[0].getBoundingClientRect();
    const lRect = cells[cells.length - 1].getBoundingClientRect();

    const x1 = fRect.left + fRect.width  / 2 - wRect.left;
    const y1 = fRect.top  + fRect.height / 2 - wRect.top;
    const x2 = lRect.left + lRect.width  / 2 - wRect.left;
    const y2 = lRect.top  + lRect.height / 2 - wRect.top;

    const dist  = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
    const pillW = dist + fRect.width + 6;
    const pillH = fRect.height + 10;
    const cx = (x1 + x2) / 2;
    const cy = (y1 + y2) / 2;

    const el = document.createElement('div');
    el.style.cssText = [
      'position:absolute',
      `width:${pillW}px`,
      `height:${pillH}px`,
      'border-radius:999px',
      `background:${fill}`,
      `border:0px solid ${border}`,
      `left:${cx - pillW / 2}px`,
      `top:${cy - pillH / 2}px`,
      `transform:rotate(${angle}deg)`,
      'transform-origin:center center',
      'pointer-events:none',
    ].join(';');
    return el;
  }

  // ── Helpers ─────────────────────────────────────────────────

  function cellFromPoint(x, y) {
    const el = document.elementFromPoint(x, y);
    if (!el) return null;
    if (el.classList.contains('ws-cell')) return el;
    return el.closest?.('.ws-cell') || null;
  }

  function clearHighlight() {
    if (previewPill) { previewPill.remove(); previewPill = null; }
    gridEl.querySelectorAll('.ws-cell.selecting').forEach(c => c.classList.remove('selecting'));
    selectedCells = [];
  }

  function highlightLine(from, to) {
    clearHighlight();
    const r1 = parseInt(from.dataset.r), c1 = parseInt(from.dataset.c);
    const r2 = parseInt(to.dataset.r),   c2 = parseInt(to.dataset.c);
    const dr = r2 - r1, dc = c2 - c1;
    if (dr !== 0 && dc !== 0 && Math.abs(dr) !== Math.abs(dc)) return;
    const len   = Math.max(Math.abs(dr), Math.abs(dc));
    const stepR = dr === 0 ? 0 : dr / Math.abs(dr);
    const stepC = dc === 0 ? 0 : dc / Math.abs(dc);
    for (let i = 0; i <= len; i++) {
      const cell = gridEl.querySelector(`[data-r="${r1 + stepR * i}"][data-c="${c1 + stepC * i}"]`);
      if (cell) {
        if (!cell.classList.contains('found')) cell.classList.add('selecting');
        selectedCells.push(cell);
      }
    }
    if (selectedCells.length > 0) {
      previewPill = buildPill(selectedCells, 'rgba(108,99,255,0.25)', 'rgba(108,99,255,0.6)');
      overlaysEl.appendChild(previewPill);
    }
  }

  // ── Mode toggle ─────────────────────────────────────────────

  window.setSearchMode = function(mode) {
    currentMode = mode;
    clearHighlight();
    startCell = null;
    document.querySelectorAll('.ws-mode-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.mode === mode);
    });
  };

  // ── Mouse — drag mode ────────────────────────────────────────

  gridEl.addEventListener('mousedown', e => {
    if (currentMode !== 'drag') return;
    const cell = cellFromPoint(e.clientX, e.clientY);
    if (!cell) return;
    e.preventDefault();
    selecting = true;
    startCell = cell;
    highlightLine(cell, cell);
  });

  document.addEventListener('mousemove', e => {
    if (!selecting || currentMode !== 'drag') return;
    const cell = cellFromPoint(e.clientX, e.clientY);
    if (!cell) return;
    highlightLine(startCell, cell);
  });

  document.addEventListener('mouseup', () => {
    if (!selecting || currentMode !== 'drag') return;
    selecting = false;
    checkSelection();
  });

  // ── Mouse — click-click mode ─────────────────────────────────

  gridEl.addEventListener('click', e => {
    if (currentMode !== 'click') return;
    const cell = cellFromPoint(e.clientX, e.clientY);
    if (!cell) return;
    if (!startCell) {
      startCell = cell;
      cell.classList.add('selecting');
      selectedCells = [cell];
      previewPill = buildPill([cell, cell], 'rgba(108,99,255,0.25)', 'rgba(108,99,255,0.6)');
      overlaysEl.appendChild(previewPill);
    } else {
      highlightLine(startCell, cell);
      checkSelection();
      startCell = null;
    }
  });

  // ── Touch ────────────────────────────────────────────────────

  gridEl.addEventListener('touchstart', e => {
    if (currentMode !== 'drag') return;
    const t = e.touches[0];
    const cell = cellFromPoint(t.clientX, t.clientY);
    if (!cell) return;
    e.preventDefault();
    selecting = true;
    startCell = cell;
    highlightLine(cell, cell);
  }, { passive: false });

  gridEl.addEventListener('touchmove', e => {
    if (!selecting || currentMode !== 'drag') return;
    e.preventDefault();
    const t = e.touches[0];
    const cell = cellFromPoint(t.clientX, t.clientY);
    if (!cell) return;
    highlightLine(startCell, cell);
  }, { passive: false });

  gridEl.addEventListener('touchend', () => {
    if (!selecting || currentMode !== 'drag') return;
    selecting = false;
    checkSelection();
  });

  // ── Vocab map: UPPERCASED-NO-SPACES → item ───────────────────
  const vocabMap = {};
  vocabulary.forEach(item => {
    const key = item.word_en.toUpperCase().replace(/\s/g, '');
    vocabMap[key] = item;
  });

  // ── Ghost image apparition ───────────────────────────────────
  function showGhostImage(word) {
    const item = vocabMap[word];
    if (!item || (!item.image && !item.emoji)) return;

    const ghost = document.createElement('div');
    ghost.className = 'ws-ghost';

    if (item.image) {
      ghost.innerHTML = `<img src="${item.image}" alt="${item.word_en}">`;
    } else {
      ghost.innerHTML = `<span class="ws-ghost-emoji">${item.emoji}</span>`;
    }

    document.body.appendChild(ghost);

    // Fade in (double rAF forces the initial style to be painted first)
    requestAnimationFrame(() => requestAnimationFrame(() => {
      ghost.classList.add('ws-ghost--in');
    }));

    // Fade out after 700 ms, then remove
    setTimeout(() => {
      ghost.classList.remove('ws-ghost--in');
      ghost.classList.add('ws-ghost--out');
      setTimeout(() => ghost.remove(), 460);
    }, 700);
  }

  // ── Word check ───────────────────────────────────────────────

  function checkSelection() {
    const text     = selectedCells.map(c => c.textContent).join('');
    const reversed = text.split('').reverse().join('');
    const match = placedWords.find(p =>
      (p.word === text || p.word === reversed) && !foundWords.has(p.word)
    );

    if (match) {
      foundWords.add(match.word);
      const color = COLORS[colorIndex % COLORS.length];
      colorIndex++;

      // Remove preview and draw permanent solid pill
      if (previewPill) { previewPill.remove(); previewPill = null; }
      const pill = buildPill(selectedCells, color, color);
      pill.style.opacity = '0';
      pill.style.transition = 'opacity 0.2s ease';
      overlaysEl.appendChild(pill);
      requestAnimationFrame(() => { pill.style.opacity = '1'; });

      // Mark cells logically found
      selectedCells.forEach(c => {
        c.classList.remove('selecting');
        c.classList.add('found');
      });

      // Update word chip
      const chip = wordListEl.querySelector(`[data-word="${match.word}"]`);
      if (chip) {
        chip.classList.add('found');
        chip.style.background = color;
        chip.style.color = 'white';
        chip.style.borderColor = color;
      }

      score += ptsPerAction;
      foundCountEl.textContent = foundWords.size;
      if (scoreDisplay) scoreDisplay.textContent = score;
      showScoreToast(ptsPerAction, true);
      showGhostImage(match.word);

      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(match.word.toLowerCase());
        u.lang = 'en-US';
        speechSynthesis.speak(u);
      }

      if (foundWords.size === placedWords.length) {
        setTimeout(() => {
          window.timeSpent = timer ? timer.getElapsed() : 0;
          const _wsMax = placedWords.length * ptsPerAction;
          showWinScreen(_wsMax > 0 ? Math.round((score / _wsMax) * pointsReward) : 0, pointsReward, gameId);
        }, 500);
      }
    } else {
      clearHighlight();
    }

    selectedCells = [];
    if (currentMode === 'click') startCell = null;
  }

  // ── Timer ────────────────────────────────────────────────────

  let timer = null;
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => {
      window.timeSpent = timeLimit;
      const _wsMaxT = placedWords.length * ptsPerAction;
      showWinScreen(_wsMaxT > 0 ? Math.round((score / _wsMaxT) * pointsReward) : 0, pointsReward, gameId);
    });
    timer.start();
  }
}
