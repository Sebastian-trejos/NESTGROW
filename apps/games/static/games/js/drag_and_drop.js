// ============================================================
// NESTGROW - Drag and Drop Game
// ============================================================

function initDragAndDrop(vocabulary, gameId, timeLimit, pointsReward) {
  const items = vocabulary.slice(0, 6); // Max 6 items
  if (items.length === 0) return;

  const dropZonesEl = document.getElementById('dropZones');
  const draggablesEl = document.getElementById('draggables');
  const scoreDisplay = document.getElementById('scoreDisplay');
  const maxScoreEl = document.getElementById('maxScore');
  const checkBtn = document.getElementById('checkBtn');

  maxScoreEl.textContent = items.length;
  let correctAnswers = {};
  let score = 0;
  let timer = null;

  // Shuffle helper
  function shuffle(arr) {
    return [...arr].sort(() => Math.random() - 0.5);
  }

  // Build drop zones (images)
  items.forEach(item => {
    const col = document.createElement('div');
    col.className = 'col-6';
    col.innerHTML = `
      <div class="text-center">
        ${item.image
          ? `<img src="${item.image}" alt="${item.word_en}" class="rounded-3 mb-2" style="width:100%;max-height:110px;object-fit:cover">`
          : `<div class="rounded-3 mb-2 d-flex align-items-center justify-content-center fw-bold"
                  style="height:90px;background:#f0eeff;font-size:2rem;color:var(--primary)">
               ${item.word_en[0]}
             </div>`
        }
        <div class="drop-zone" data-id="${item.id}" data-answer="${item.word_en}">
          Drop here / Suelta aquí
        </div>
      </div>`;
    dropZonesEl.appendChild(col);
  });

  // Build draggable words (shuffled)
  shuffle(items).forEach(item => {
    const el = document.createElement('div');
    el.className = 'draggable-item';
    el.draggable = true;
    el.dataset.word = item.word_en;
    el.dataset.id = item.id;
    el.textContent = item.word_en;
    el.addEventListener('dragstart', onDragStart);
    el.addEventListener('touchstart', onTouchStart, { passive: false });
    draggablesEl.appendChild(el);
  });

  // Drag events
  let draggedEl = null;

  function onDragStart(e) {
    draggedEl = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', e.target.dataset.word);
  }

  document.querySelectorAll('.drop-zone').forEach(zone => {
    zone.addEventListener('dragover', e => {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      if (draggedEl) {
        if (draggedEl.classList.contains('dragging')) draggedEl.classList.remove('dragging');
        zone.dataset.dropped = draggedEl.dataset.word;
        zone.textContent = draggedEl.dataset.word;
        zone.style.fontFamily = "'Fredoka One', cursive";
        zone.style.fontSize = '1.1rem';
        zone.style.color = 'var(--primary)';
        // Hide dragged element
        draggedEl.style.opacity = '0.3';
        draggedEl.style.pointerEvents = 'none';
      }
      checkAllFilled();
    });
  });

  // Touch support (mobile)
  let touchItem = null;
  function onTouchStart(e) {
    touchItem = e.currentTarget;
  }

  function checkAllFilled() {
    const zones = document.querySelectorAll('.drop-zone');
    const allFilled = [...zones].every(z => z.dataset.dropped);
    if (allFilled) checkBtn.style.display = 'inline-block';
  }

  // Check answers
  checkBtn.addEventListener('click', () => {
    score = 0;
    const zones = document.querySelectorAll('.drop-zone');
    zones.forEach(zone => {
      if (zone.dataset.dropped === zone.dataset.answer) {
        zone.classList.add('correct');
        score++;
      } else {
        zone.classList.add('incorrect');
        setTimeout(() => zone.classList.remove('incorrect'), 600);
      }
    });
    scoreDisplay.textContent = score;
    if (timer) timer.stop();
    const elapsed = timer ? timer.getElapsed() : 0;
    window.timeSpent = elapsed;
    setTimeout(() => showWinScreen(score * pointsReward, items.length * pointsReward, gameId), 800);
  });

  // Timer
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => {
      checkBtn.click();
    });
    timer.start();
  }
}
