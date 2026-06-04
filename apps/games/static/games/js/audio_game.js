// ============================================================
// NESTGROW - Audio Bingo (Bombo)
// Dificultad 1 (Fácil):   4 palabras, velocidad normal
// Dificultad 2 (Medio):   6 palabras, velocidades aleatorias + shuffle cada 3 aciertos
// Dificultad 3 (Difícil): 9 palabras, lo mismo + 1-3 palabras en cadena por giro
// ============================================================

function initAudioGame(vocabulary, gameId, pointsReward, penaltyAmount, difficulty) {
  if (!vocabulary || vocabulary.length === 0) return;
  difficulty = parseInt(difficulty) || 1;

  // ── Config by difficulty ──────────────────────────────────
  const CARD_SIZES   = { 1: 8, 2: 10, 3: 14 };
  const AUDIO_SPEEDS = [0.62, 0.85, 1.15]; // for medio/difícil
  const SHUFFLE_EVERY = 3;                 // correct answers before card shuffle

  const cardSize    = Math.min(CARD_SIZES[difficulty] || 4, vocabulary.length);
  const ptsPerAction = Math.max(1, Math.round(pointsReward / cardSize));

  // Pick random vocabulary for this card
  const cardItems = [...vocabulary]
    .sort(() => Math.random() - 0.5)
    .slice(0, cardSize);

  // ── State ─────────────────────────────────────────────────
  let score                  = 0;
  let foundCount             = 0;
  let bomboReady             = true;
  let waitingForSelection    = false;
  let currentBatch           = []; // array of cardState indices to find
  let correctSinceLastShuffle = 0;

  // cardState: array of { item, found, cellEl }
  const cardState = cardItems.map(item => ({ item, found: false, cellEl: null }));

  // ── DOM ───────────────────────────────────────────────────
  const scoreDisplay  = document.getElementById('scoreDisplay');
  const foundCountEl  = document.getElementById('foundCount');
  const totalCountEl  = document.getElementById('totalCount');
  const bingoGrid     = document.getElementById('abBingoGrid');
  const hintMsg       = document.getElementById('hintMsg');
  const abDrum        = document.getElementById('abDrum');
  const abSpinBtn     = document.getElementById('abSpinBtn');
  const bubbleZone    = document.getElementById('abBubbleZone');
  const batchBox      = document.getElementById('abBatchBox');
  const batchWords    = document.getElementById('abBatchWords');

  totalCountEl.textContent = cardSize;

  // ── Grid columns & cell sizing ────────────────────────────
  // Fácil→4 cols (4×2), Medio→5 cols (5×2), Difícil→7 cols (7×2)
  const cols = difficulty === 1 ? 4 : difficulty === 2 ? 5 : 7;
  bingoGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  bingoGrid.style.gap = difficulty >= 3 ? '6px' : '10px';
  // Inject per-difficulty cell size overrides
  const cellStyle = document.createElement('style');
  cellStyle.textContent = difficulty >= 3
    ? `.ab-cell { min-height:95px; padding:5px; }
       .ab-cell img { height:72px; }
       .ab-cell-word-big { font-size:0.88rem; }`
    : difficulty === 2
    ? `.ab-cell { min-height:108px; padding:6px; }
       .ab-cell img { height:84px; }
       .ab-cell-word-big { font-size:0.95rem; }`
    : '';
  if (cellStyle.textContent) document.head.appendChild(cellStyle);

  // ── Render bingo card ─────────────────────────────────────
  function renderCard() {
    bingoGrid.innerHTML = '';
    cardState.forEach((state, idx) => {
      const cell = document.createElement('div');
      cell.className = 'ab-cell';
      cell.dataset.idx = idx;

      if (state.item.image) {
        cell.innerHTML = `<img src="${state.item.image}" alt="${state.item.word_en}">`;
      } else {
        cell.innerHTML = `<div class="ab-cell-word-big">${state.item.word_en}</div>`;
      }

      if (state.found) {
        cell.classList.add('ab-cell-found');
        const check = document.createElement('div');
        check.className = 'ab-cell-check';
        check.style.animation = 'none'; // no pop on re-render
        check.textContent = '✔';
        cell.appendChild(check);
      }

      cell.addEventListener('click', () => onCellClick(idx));
      state.cellEl = cell;
      bingoGrid.appendChild(cell);
    });
  }

  renderCard();

  // ── Audio helpers ─────────────────────────────────────────
  function pickSpeed() {
    if (difficulty <= 1) return 0.85;
    return AUDIO_SPEEDS[Math.floor(Math.random() * AUDIO_SPEEDS.length)];
  }

  function speakWord(word, rate) {
    return new Promise(resolve => {
      let done = false;
      const finish = () => { if (!done) { done = true; resolve(); } };
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(word);
        u.lang  = 'en-US';
        u.rate  = rate || 0.85;
        u.pitch = 1.05;
        u.onend   = finish;
        u.onerror = finish;
        window.speechSynthesis.speak(u);
        // Fallback in case onend never fires
        setTimeout(finish, Math.max(2200, (word.length * 130) / (rate || 0.85)));
      } else {
        setTimeout(finish, 700);
      }
    });
  }

  function playWordAudio(item, rate) {
    return new Promise(resolve => {
      let done = false;
      const finish = () => { if (!done) { done = true; resolve(); } };
      if (item.audio) {
        const audio = new Audio(item.audio);
        audio.playbackRate = rate || 1.0;
        audio.onended = finish;
        audio.onerror  = () => speakWord(item.word_en, rate).then(finish);
        audio.play().catch(() => speakWord(item.word_en, rate).then(finish));
        setTimeout(finish, 5000);
      } else {
        speakWord(item.word_en, rate).then(finish);
      }
    });
  }

  // ── Bombo spin animation ──────────────────────────────────
  function spinDrum() {
    return new Promise(resolve => {
      let done = false;
      const finish = () => { if (!done) { done = true; resolve(); } };
      abDrum.classList.remove('spinning');
      void abDrum.offsetWidth; // force reflow to restart animation
      abDrum.classList.add('spinning');
      abDrum.addEventListener('animationend', () => {
        abDrum.classList.remove('spinning');
        finish();
      }, { once: true });
      setTimeout(finish, 1200); // fallback
    });
  }

  // ── Bubble animation ──────────────────────────────────────
  function spawnBubble() {
    const b = document.createElement('div');
    b.className = 'ab-bubble';
    b.textContent = '🔊';
    bubbleZone.appendChild(b);
    setTimeout(() => b.remove(), 1500);
  }

  // ── Pick batch for this spin ──────────────────────────────
  function pickBatch() {
    const available = cardState
      .map((s, i) => i)
      .filter(i => !cardState[i].found);
    if (available.length === 0) return [];

    let size = 1;
    if (difficulty >= 3) {
      const maxSize = Math.min(3, available.length);
      size = Math.floor(Math.random() * maxSize) + 1;
    }
    return [...available].sort(() => Math.random() - 0.5).slice(0, size);
  }

  // Batch UI and cell highlights intentionally disabled —
  // showing hints would reveal the answers to students.
  function updateBatchUI() { batchBox.style.display = 'none'; }
  function refreshCellHighlights() {}

  // ── Delay helper ──────────────────────────────────────────
  function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ── Main: trigger bombo ───────────────────────────────────
  async function triggerBombo() {
    if (!bomboReady || waitingForSelection) return;

    bomboReady          = false;
    waitingForSelection = false;
    abSpinBtn.disabled  = true;

    // 1. Spin
    await spinDrum();

    // 2. Pick batch
    currentBatch = pickBatch();
    if (currentBatch.length === 0) { endGame(); return; }

    // 3. Play audio chain
    const speed = pickSpeed();
    for (let i = 0; i < currentBatch.length; i++) {
      spawnBubble();
      await wait(220);
      await playWordAudio(cardState[currentBatch[i]].item, speed);
      if (i < currentBatch.length - 1) {
        await wait(550);
      }
    }

    // 4. Activate selection mode
    waitingForSelection = true;

    if (currentBatch.length > 1) {
      hintMsg.textContent = `Listen to the ${currentBatch.length} words and find them all!`;
    } else {
      hintMsg.textContent = '🎯 Find that word on your card!';
    }

    updateBatchUI();
    refreshCellHighlights();
  }

  // ── Cell click handler ────────────────────────────────────
  function onCellClick(idx) {
    if (!waitingForSelection) return;
    const state = cardState[idx];
    if (state.found) return;

    const isInBatch = currentBatch.includes(idx);

    if (isInBatch) {
      // ✅ Correct
      state.found = true;
      foundCount++;
      correctSinceLastShuffle++;
      score += ptsPerAction;
      scoreDisplay.textContent = score;
      foundCountEl.textContent = foundCount;
      showScoreToast(ptsPerAction, true);

      state.cellEl.classList.remove('ab-cell-active', 'ab-cell-wrong');
      state.cellEl.classList.add('ab-cell-found');
      const check = document.createElement('div');
      check.className = 'ab-cell-check';
      check.textContent = '✔';
      state.cellEl.appendChild(check);

      hintMsg.textContent = `✅ Correct! "${state.item.word_en}" means "${state.item.word_es}"`;
      updateBatchUI();

      // Win?
      if (foundCount >= cardSize) {
        waitingForSelection = false;
        refreshCellHighlights();
        batchBox.style.display = 'none';
        setTimeout(endGame, 700);
        return;
      }

      // Batch complete?
      const remaining = currentBatch.filter(i => !cardState[i].found);
      if (remaining.length === 0) {
        waitingForSelection = false;
        currentBatch = [];
        batchBox.style.display = 'none';
        refreshCellHighlights();

        if (difficulty >= 2 && correctSinceLastShuffle >= SHUFFLE_EVERY) {
          correctSinceLastShuffle = 0;
          setTimeout(async () => {
            hintMsg.textContent = '🔀 Shuffling the cards!';
            await triggerShuffle();
            bomboReady = true;
            abSpinBtn.disabled = false;
            hintMsg.textContent = 'Cards shuffled! Spin the drum again.';
          }, 500);
        } else {
          bomboReady = true;
          abSpinBtn.disabled = false;
          hintMsg.textContent = 'Nice! Spin the drum to continue.';
        }
      } else {
        // More in batch to find
        refreshCellHighlights();
        updateBatchUI();
      }

    } else {
      // ❌ Wrong
      score = Math.max(0, score - penaltyAmount);
      scoreDisplay.textContent = score;
      showScoreToast(penaltyAmount, false);
      showOopsToast();

      state.cellEl.classList.add('ab-cell-wrong');
      const xEl = document.createElement('div');
      xEl.className = 'ab-cell-x';
      xEl.textContent = '✗';
      state.cellEl.appendChild(xEl);
      setTimeout(() => {
        state.cellEl.classList.remove('ab-cell-wrong');
        xEl.remove();
      }, 650);

      hintMsg.textContent = "❌ Oops! That's not it — try again!";
    }
  }

  // ── Card shuffle (medio/difícil) ──────────────────────────
  async function triggerShuffle() {
    // Fade out non-found cells
    const nonFoundStates = cardState.filter(s => !s.found);
    nonFoundStates.forEach(s => {
      if (!s.cellEl) return;
      s.cellEl.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
      s.cellEl.style.opacity    = '0';
      s.cellEl.style.transform  = 'scale(0.78)';
    });
    await wait(400);

    // Rearrange non-found items
    const nfIndices = cardState.map((s, i) => i).filter(i => !cardState[i].found);
    const nfItems   = nfIndices.map(i => cardState[i].item);
    const shuffled  = [...nfItems].sort(() => Math.random() - 0.5);
    nfIndices.forEach((origIdx, i) => { cardState[origIdx].item = shuffled[i]; });

    // Re-render
    renderCard();

    // Fade in
    cardState.forEach(s => {
      if (!s.found && s.cellEl) {
        s.cellEl.style.transition = 'none';
        s.cellEl.style.opacity    = '0';
        s.cellEl.style.transform  = 'scale(0.78)';
      }
    });
    await wait(40);
    cardState.forEach(s => {
      if (!s.found && s.cellEl) {
        s.cellEl.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        s.cellEl.style.opacity    = '1';
        s.cellEl.style.transform  = 'scale(1)';
      }
    });
    await wait(450);
    cardState.forEach(s => {
      if (s.cellEl) {
        s.cellEl.style.transition = '';
        s.cellEl.style.opacity    = '';
        s.cellEl.style.transform  = '';
      }
    });
  }

  // ── Oops toast ────────────────────────────────────────────
  function showOopsToast() {
    const el = document.createElement('div');
    el.className = 'ab-oops-toast';
    el.textContent = '😬 Oops! Wrong card!';
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1350);
  }

  // ── End game ──────────────────────────────────────────────
  function endGame() {
    window.timeSpent = 0;
    const _agMax = cardSize * ptsPerAction;
    showWinScreen(_agMax > 0 ? Math.round((score / _agMax) * pointsReward) : 0, pointsReward, gameId);
  }

  // ── Wire up events ────────────────────────────────────────
  abSpinBtn.addEventListener('click', triggerBombo);
  abDrum.addEventListener('click', triggerBombo);

  // Ready
  hintMsg.textContent = 'Spin the drum to hear a word!';
}
