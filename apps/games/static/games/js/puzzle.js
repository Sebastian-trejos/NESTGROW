// ============================================================
// NESTGROW - Rompecabezas Jigsaw
// Cada vocabulario item con imagen = un puzzle independiente.
// Grid: dificultad 1=3x3, 2=4x4, 3=5x5
// ============================================================

function initPuzzle(vocabulary, gameId, timeLimit, pointsReward, difficulty, penaltyAmount) {
  const PUZZLE_PENALTY = 1; // Penalidad fija por pieza mal colocada (bajo por ser exploración)
  const GRID_SIZE  = difficulty === 3 ? 5 : difficulty === 2 ? 4 : 3;
  const PIECE_SIZE = Math.min(Math.floor(480 / GRID_SIZE), 110);
  const TOTAL_PIECES = GRID_SIZE * GRID_SIZE;

  // Solo items con imagen
  const images = vocabulary
    .filter(v => v.image)
    .map(v => ({ id: v.id, name: v.word_en, url: v.image }));

  const ptsPerAction = Math.max(1, Math.round(pointsReward / Math.max(1, images.length)));

  let currentIndex   = 0;
  let correctCount   = 0;
  let totalScore     = 0;
  let draggedPiece   = null;
  let timer          = null;

  const boardEl  = document.getElementById('puzzleBoard');
  const piecesEl = document.getElementById('puzzlePieces');
  const nameEl   = document.getElementById('puzzleName');
  const counterEl = document.getElementById('puzzleCounter');

  // ── Sin imágenes ────────────────────────────────────────────
  if (!images.length) {
    nameEl.textContent    = 'Sin imágenes disponibles';
    counterEl.textContent = 'El profesor debe añadir imágenes con vocabulario';
    return;
  }

  // ── Timer ────────────────────────────────────────────────────
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    if (timerEl) {
      timer = new GameTimer(timeLimit, timerEl, () => {
        window.timeSpent = timeLimit;
        showWinScreen(totalScore, images.length * ptsPerAction, gameId);
      });
      timer.start();
    }
  }

  // ── Carga una imagen y construye el puzzle ───────────────────
  function loadPuzzle(index) {
    const img = images[index];
    nameEl.textContent    = img.name;
    counterEl.textContent = `Imagen ${index + 1} de ${images.length}`;
    correctCount = 0;
    buildPuzzle(img.url);
  }

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function buildPuzzle(imageUrl) {
    boardEl.innerHTML  = '';
    piecesEl.innerHTML = '';
    boardEl.style.gridTemplateColumns = `repeat(${GRID_SIZE}, ${PIECE_SIZE}px)`;

    // Crear celdas vacías
    for (let i = 0; i < TOTAL_PIECES; i++) {
      const cell = document.createElement('div');
      cell.className   = 'puzzle-cell';
      cell.style.width  = PIECE_SIZE + 'px';
      cell.style.height = PIECE_SIZE + 'px';
      cell.dataset.index = i;

      cell.addEventListener('dragover',  e => { e.preventDefault(); cell.classList.add('drag-over'); });
      cell.addEventListener('dragleave', ()  => cell.classList.remove('drag-over'));
      cell.addEventListener('drop',      e  => { e.preventDefault(); cell.classList.remove('drag-over'); dropPiece(cell); });
      cell.addEventListener('touchend',  e  => { e.preventDefault(); cell.classList.remove('drag-over'); dropPiece(cell); });
      boardEl.appendChild(cell);
    }

    // Crear piezas mezcladas
    const indices = shuffle([...Array(TOTAL_PIECES).keys()]);
    indices.forEach(i => {
      const row = Math.floor(i / GRID_SIZE);
      const col = i % GRID_SIZE;
      const piece = document.createElement('div');
      piece.className   = 'puzzle-piece';
      piece.dataset.correct = i;
      piece.style.width  = PIECE_SIZE + 'px';
      piece.style.height = PIECE_SIZE + 'px';
      piece.style.backgroundImage    = `url(${imageUrl})`;
      piece.style.backgroundSize     = `${GRID_SIZE * PIECE_SIZE}px ${GRID_SIZE * PIECE_SIZE}px`;
      piece.style.backgroundPosition = `-${col * PIECE_SIZE}px -${row * PIECE_SIZE}px`;
      piece.draggable = true;

      // Drag (desktop)
      piece.addEventListener('dragstart', e => {
        draggedPiece = piece;
        setTimeout(() => piece.classList.add('dragging'), 0);
        e.dataTransfer.effectAllowed = 'move';
      });
      piece.addEventListener('dragend', () => piece.classList.remove('dragging'));

      // Touch drag
      piece.addEventListener('touchstart', () => {
        draggedPiece = piece;
        piece.classList.add('dragging');
      }, { passive: true });

      piece.addEventListener('touchmove', e => {
        e.preventDefault();
        const touch = e.touches[0];
        boardEl.querySelectorAll('.puzzle-cell').forEach(c => c.classList.remove('drag-over'));
        const el = document.elementFromPoint(touch.clientX, touch.clientY);
        if (el?.classList.contains('puzzle-cell')) el.classList.add('drag-over');
      }, { passive: false });

      piece.addEventListener('touchend', e => {
        piece.classList.remove('dragging');
        const touch = e.changedTouches[0];
        boardEl.querySelectorAll('.puzzle-cell').forEach(c => c.classList.remove('drag-over'));
        const el = document.elementFromPoint(touch.clientX, touch.clientY);
        const target = el?.classList.contains('puzzle-cell') ? el : el?.closest('.puzzle-cell');
        if (target) dropPiece(target);
      });

      piecesEl.appendChild(piece);
    });
  }

  // ── Soltar pieza en celda ────────────────────────────────────
  function dropPiece(cell) {
    if (!draggedPiece) return;
    if (cell.contains(draggedPiece)) { draggedPiece = null; return; }

    const cellIndex   = parseInt(cell.dataset.index);
    const pieceCorrect = parseInt(draggedPiece.dataset.correct);

    // Si la celda ya tiene una pieza diferente, devolverla al área
    const existing = cell.querySelector('.puzzle-piece');
    if (existing && existing !== draggedPiece) {
      existing.style.width  = PIECE_SIZE + 'px';
      existing.style.height = PIECE_SIZE + 'px';
      existing.classList.remove('dragging');
      piecesEl.appendChild(existing);
      if (cell.classList.contains('correct')) correctCount--;
      cell.classList.remove('correct');
    }

    // Limpiar celda de origen si venía de otra celda
    const oldParent = draggedPiece.parentElement;
    if (oldParent?.classList.contains('puzzle-cell') && oldParent !== cell) {
      if (oldParent.classList.contains('correct')) correctCount--;
      oldParent.classList.remove('correct');
    }

    // Colocar pieza
    draggedPiece.style.width  = '100%';
    draggedPiece.style.height = '100%';
    draggedPiece.classList.remove('dragging');
    cell.appendChild(draggedPiece);

    if (pieceCorrect === cellIndex) {
      cell.classList.add('correct');
      correctCount++;
    } else {
      cell.classList.remove('correct');
      totalScore = Math.max(0, totalScore - PUZZLE_PENALTY);
      showScoreToast(PUZZLE_PENALTY, false);
      const sd = document.getElementById('scoreDisplay');
      if (sd) sd.textContent = totalScore;
    }
    draggedPiece = null;
  }

  // ── Verificar manualmente ────────────────────────────────────
  window.checkPuzzleComplete = function() {
    if (correctCount === TOTAL_PIECES) {
      celebrateImage();
    } else {
      document.getElementById('errorMsg').textContent =
        `Llevas ${correctCount} de ${TOTAL_PIECES} piezas en su lugar. ¡Tú puedes!`;
      bootstrap.Modal.getOrCreateInstance(document.getElementById('errorModal')).show();
    }
  };

  // ── Mezclar de nuevo ─────────────────────────────────────────
  window.shufflePieces = function() { loadPuzzle(currentIndex); };

  // ── Completó una imagen ──────────────────────────────────────
  function celebrateImage() {
    totalScore += ptsPerAction;
    showScoreToast(ptsPerAction, true);
    const sd = document.getElementById('scoreDisplay');
    if (sd) sd.textContent = totalScore;
    const img    = images[currentIndex];
    const isLast = currentIndex >= images.length - 1;

    if (isLast) {
      // Último puzzle → win screen estándar
      if (timer) timer.stop();
      window.timeSpent = timer ? timer.getElapsed() : 0;
      showWinScreen(totalScore, images.length * ptsPerAction, gameId);
      return;
    }

    // Puzzle intermedio → modal "siguiente"
    document.getElementById('nextTitle').textContent = `¡"${img.name}" armado! 🎉`;
    document.getElementById('nextMsg').textContent =
      `Siguiente: "${images[currentIndex + 1].name}"`;
    document.getElementById('nextButtons').innerHTML = `
      <button class="btn btn-nestgrow btn-primary-nestgrow" onclick="goNextPuzzle()">Siguiente 🧩</button>
      <a href="${window.PUZZLE_GAME_LIST_URL || '/juegos/'}" class="btn btn-outline-secondary rounded-pill">Salir</a>`;
    bootstrap.Modal.getOrCreateInstance(document.getElementById('nextModal')).show();
  }

  window.goNextPuzzle = function() {
    bootstrap.Modal.getInstance(document.getElementById('nextModal')).hide();
    currentIndex++;
    loadPuzzle(currentIndex);
  };

  // ── Inicio ───────────────────────────────────────────────────
  loadPuzzle(0);
}
