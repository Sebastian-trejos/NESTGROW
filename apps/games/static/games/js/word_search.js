// ============================================================
// NESTGROW - Word Search Game
// ============================================================

function initWordSearch(vocabulary, gameId, timeLimit, pointsReward) {
  const GRID_SIZE = 10;
  const words = vocabulary.map(v => v.word_en.toUpperCase().replace(/\s/g, '')).slice(0, 8);
  const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  let grid = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(''));
  let placedWords = [];
  const directions = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[1,-1],[-1,1]];

  // Place words
  words.forEach(word => {
    let placed = false;
    for (let attempt = 0; attempt < 150 && !placed; attempt++) {
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

  // Render grid
  const gridEl = document.getElementById('wsGrid');
  gridEl.style.gridTemplateColumns = `repeat(${GRID_SIZE}, 1fr)`;
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

  // Render word list
  const wordListEl = document.getElementById('wordList');
  const totalWordsEl = document.getElementById('totalWords');
  const foundCountEl = document.getElementById('foundCount');
  const scoreDisplay = document.getElementById('scoreDisplay');
  totalWordsEl.textContent = placedWords.length;

  const wordEls = {};
  placedWords.forEach(({ word }) => {
    const div = document.createElement('div');
    div.className = 'd-flex align-items-center gap-2';
    div.innerHTML = `<span class="fw-bold" style="color:var(--primary)">${word}</span>`;
    wordListEl.appendChild(div);
    wordEls[word] = div;
  });

  // Selection logic
  let selecting = false;
  let selectedCells = [];
  let foundWords = new Set();
  let score = 0;

  function getCellKey(r, c) { return `${r}-${c}`; }

  gridEl.addEventListener('mousedown', e => {
    if (!e.target.classList.contains('ws-cell')) return;
    selecting = true;
    selectedCells = [];
    highlightCell(e.target, true);
  });

  gridEl.addEventListener('mousemove', e => {
    if (!selecting || !e.target.classList.contains('ws-cell')) return;
    const key = getCellKey(e.target.dataset.r, e.target.dataset.c);
    if (!selectedCells.find(k => k === key)) {
      selectedCells.push(key);
      highlightCell(e.target, true);
    }
  });

  document.addEventListener('mouseup', () => {
    if (!selecting) return;
    selecting = false;
    checkSelection();
    clearSelection();
  });

  function highlightCell(cell, on) {
    cell.classList.toggle('selected', on);
  }

  function clearSelection() {
    gridEl.querySelectorAll('.ws-cell.selected').forEach(c => c.classList.remove('selected'));
    selectedCells = [];
  }

  function checkSelection() {
    const cells = gridEl.querySelectorAll('.ws-cell.selected');
    const letters = [...cells].map(c => c.textContent).join('');
    const reversed = letters.split('').reverse().join('');
    const match = placedWords.find(p => (p.word === letters || p.word === reversed) && !foundWords.has(p.word));
    if (match) {
      foundWords.add(match.word);
      cells.forEach(c => { c.classList.remove('selected'); c.classList.add('found'); });
      // Mark word list
      const wordEl = wordEls[match.word];
      if (wordEl) {
        wordEl.innerHTML = `<span class="fw-bold text-success text-decoration-line-through">${match.word}</span> ✅`;
      }
      score += pointsReward;
      foundCountEl.textContent = foundWords.size;
      scoreDisplay.textContent = score;
      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(match.word.toLowerCase());
        u.lang = 'en-US';
        speechSynthesis.speak(u);
      }
      if (foundWords.size === placedWords.length) {
        setTimeout(() => {
          window.timeSpent = timer ? timer.getElapsed() : 0;
          showWinScreen(score, placedWords.length * pointsReward, gameId);
        }, 500);
      }
    }
  }

  // Timer
  let timer = null;
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => {
      window.timeSpent = timeLimit;
      showWinScreen(score, placedWords.length * pointsReward, gameId);
    });
    timer.start();
  }
}
