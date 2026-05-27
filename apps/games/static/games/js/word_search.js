// ============================================================
// NESTGROW - Word Search Game
// Grid size varies by difficulty: easy=8x8, medium=12x12, hard=16x16
// Words come automatically from the game's vocabulary category
// ============================================================

function initWordSearch(vocabulary, gameId, timeLimit, pointsReward, difficulty, penaltyAmount) {
  const GRID_SIZE = difficulty === 3 ? 16 : difficulty === 2 ? 12 : 8;
  const MAX_WORDS = difficulty === 3 ? 12 : difficulty === 2 ? 8 : 5;
  const COLORS = ['#e74c3c','#3498db','#2ecc71','#9b59b6','#f39c12','#1abc9c','#e91e63','#ff5722'];

  const words = vocabulary.map(v => v.word_en.toUpperCase().replace(/\s/g, '')).filter(w => w.length >= 2 && w.length <= GRID_SIZE).slice(0, MAX_WORDS);
  const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  let grid = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(''));
  let placedWords = [];
  const directions = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[1,-1],[-1,1]];

  // Place words
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

  // Fill blanks
  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (!grid[r][c]) grid[r][c] = ALPHABET[Math.floor(Math.random() * 26)];

  const cellSize = GRID_SIZE <= 8 ? 42 : GRID_SIZE <= 12 ? 34 : 26;
  const gridEl = document.getElementById('wsGrid');
  gridEl.style.gridTemplateColumns = `repeat(${GRID_SIZE}, 1fr)`;

  const styleEl = document.createElement('style');
  styleEl.textContent = `.ws-cell { width:${cellSize}px !important; height:${cellSize}px !important; font-size:${cellSize <= 26 ? '0.75' : cellSize <= 34 ? '0.9' : '1.1'}rem !important; }`;
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

  // Word list as chips
  const wordListEl = document.getElementById('wordList');
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

  // State
  const ptsPerAction = Math.max(1, Math.round(pointsReward / placedWords.length));

  let currentMode = 'drag';
  let selecting = false;
  let startCell = null;
  let selectedCells = [];
  let foundWords = new Set();
  let colorIndex = 0;
  let score = 0;

  // Mode toggle — called from template buttons
  window.setSearchMode = function(mode) {
    currentMode = mode;
    clearHighlight();
    startCell = null;
    document.querySelectorAll('.ws-mode-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.mode === mode);
    });
  };

  function clearHighlight() {
    gridEl.querySelectorAll('.ws-cell.selecting').forEach(c => c.classList.remove('selecting'));
    selectedCells = [];
  }

  // Constrained straight-line highlight (8 directions only)
  function highlightLine(from, to) {
    clearHighlight();
    const r1 = parseInt(from.dataset.r), c1 = parseInt(from.dataset.c);
    const r2 = parseInt(to.dataset.r), c2 = parseInt(to.dataset.c);
    const dr = r2 - r1, dc = c2 - c1;
    if (dr !== 0 && dc !== 0 && Math.abs(dr) !== Math.abs(dc)) return;
    const len = Math.max(Math.abs(dr), Math.abs(dc));
    const stepR = dr === 0 ? 0 : dr / Math.abs(dr);
    const stepC = dc === 0 ? 0 : dc / Math.abs(dc);
    for (let i = 0; i <= len; i++) {
      const cell = gridEl.querySelector(`[data-r="${r1 + stepR * i}"][data-c="${c1 + stepC * i}"]`);
      if (cell && !cell.classList.contains('found')) {
        cell.classList.add('selecting');
        selectedCells.push(cell);
      }
    }
  }

  // Drag mode
  gridEl.addEventListener('mousedown', e => {
    if (!e.target.classList.contains('ws-cell') || currentMode !== 'drag') return;
    e.preventDefault();
    selecting = true;
    startCell = e.target;
    highlightLine(startCell, startCell);
  });

  gridEl.addEventListener('mousemove', e => {
    if (!selecting || currentMode !== 'drag' || !e.target.classList.contains('ws-cell')) return;
    highlightLine(startCell, e.target);
  });

  document.addEventListener('mouseup', () => {
    if (!selecting || currentMode !== 'drag') return;
    selecting = false;
    checkSelection();
  });

  // Click-click mode
  gridEl.addEventListener('click', e => {
    if (!e.target.classList.contains('ws-cell') || currentMode !== 'click') return;
    if (!startCell) {
      startCell = e.target;
      e.target.classList.add('selecting');
      selectedCells = [e.target];
    } else {
      highlightLine(startCell, e.target);
      checkSelection();
      startCell = null;
    }
  });

  // Touch support
  gridEl.addEventListener('touchstart', e => {
    if (currentMode !== 'drag') return;
    const touch = e.touches[0];
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    if (!el?.classList.contains('ws-cell')) return;
    selecting = true;
    startCell = el;
    highlightLine(el, el);
  }, { passive: true });

  gridEl.addEventListener('touchmove', e => {
    if (!selecting || currentMode !== 'drag') return;
    const touch = e.touches[0];
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    if (!el?.classList.contains('ws-cell')) return;
    highlightLine(startCell, el);
  }, { passive: true });

  gridEl.addEventListener('touchend', () => {
    if (!selecting || currentMode !== 'drag') return;
    selecting = false;
    checkSelection();
  });

  function checkSelection() {
    const text = selectedCells.map(c => c.textContent).join('');
    const reversed = text.split('').reverse().join('');
    const match = placedWords.find(p => (p.word === text || p.word === reversed) && !foundWords.has(p.word));
    if (match) {
      foundWords.add(match.word);
      const color = COLORS[colorIndex % COLORS.length];
      colorIndex++;
      selectedCells.forEach(c => {
        c.classList.remove('selecting');
        c.classList.add('found');
        c.style.background = color;
        c.style.color = 'white';
        c.style.borderRadius = '4px';
      });
      const chip = wordListEl.querySelector(`[data-word="${match.word}"]`);
      if (chip) chip.classList.add('found');
      score += ptsPerAction;
      foundCountEl.textContent = foundWords.size;
      if (scoreDisplay) scoreDisplay.textContent = score;
      showScoreToast(ptsPerAction, true);
      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(match.word.toLowerCase());
        u.lang = 'en-US'; speechSynthesis.speak(u);
      }
      if (foundWords.size === placedWords.length) {
        setTimeout(() => {
          window.timeSpent = timer ? timer.getElapsed() : 0;
          showWinScreen(score, placedWords.length * ptsPerAction, gameId);
        }, 500);
      }
    } else {
      clearHighlight();
    }
    selectedCells = [];
    if (currentMode === 'click') startCell = null;
  }

  let timer = null;
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => {
      window.timeSpent = timeLimit;
      showWinScreen(score, placedWords.length * ptsPerAction, gameId);
    });
    timer.start();
  }
}