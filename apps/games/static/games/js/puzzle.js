// ============================================================
// NESTGROW - Puzzle / Matching Game
// Match images (left) with English words (right)
// ============================================================

function initPuzzle(vocabulary, gameId, timeLimit, pointsReward) {
  if (!vocabulary || vocabulary.length === 0) return;

  const items = [...vocabulary].sort(() => Math.random() - 0.5).slice(0, 6);
  const totalPairs = items.length;

  const imagesCol = document.getElementById('imagesColumn');
  const wordsCol = document.getElementById('wordsColumn');
  const matchedCountEl = document.getElementById('matchedCount');
  const totalPairsEl = document.getElementById('totalPairs');
  const scoreDisplay = document.getElementById('scoreDisplay');

  totalPairsEl.textContent = totalPairs;

  let selectedImage = null;
  let selectedWord = null;
  let matchedPairs = 0;
  let score = 0;
  let timer = null;

  // Shuffle helpers
  function shuffle(arr) { return [...arr].sort(() => Math.random() - 0.5); }

  // Build image cards (left column) — shuffled order
  shuffle(items).forEach(item => {
    const card = document.createElement('div');
    card.className = 'puzzle-piece';
    card.dataset.id = item.id;
    card.dataset.col = 'image';

    if (item.image) {
      card.innerHTML = `
        <img src="${item.image}" alt="${item.word_en}" class="puzzle-img">
        <div class="puzzle-word" style="color:var(--text-light);font-size:0.75rem">${item.word_es}</div>`;
    } else {
      // No image: show colored box with first letter
      const colors = ['#FF6B6B','#6C63FF','#4ECDC4','#FFE66D','#A8E6CF','#FFB347'];
      const color = colors[item.id % colors.length];
      card.innerHTML = `
        <div style="width:70px;height:60px;background:${color}20;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:4px">
          <span style="font-family:'Fredoka One',cursive;font-size:2rem;color:${color}">${item.word_en[0]}</span>
        </div>
        <div class="puzzle-word" style="color:var(--text-light);font-size:0.75rem">${item.word_es}</div>`;
    }

    card.addEventListener('click', () => handleImageClick(card, item));
    imagesCol.appendChild(card);
  });

  // Build word cards (right column) — separately shuffled
  shuffle(items).forEach(item => {
    const card = document.createElement('div');
    card.className = 'puzzle-piece';
    card.dataset.id = item.id;
    card.dataset.col = 'word';
    card.innerHTML = `
      <div class="puzzle-word" style="font-size:1.1rem;color:var(--primary);font-family:'Fredoka One',cursive">
        ${item.word_en}
      </div>`;

    card.addEventListener('click', () => handleWordClick(card, item));
    wordsCol.appendChild(card);
  });

  // --- Click handlers ---
  function handleImageClick(card, item) {
    if (card.classList.contains('matched')) return;

    // Deselect previous image selection
    imagesCol.querySelectorAll('.puzzle-piece.selected').forEach(c => c.classList.remove('selected'));

    selectedImage = { card, item };
    card.classList.add('selected');

    if (selectedWord) checkMatch();
  }

  function handleWordClick(card, item) {
    if (card.classList.contains('matched')) return;

    // Deselect previous word selection
    wordsCol.querySelectorAll('.puzzle-piece.selected').forEach(c => c.classList.remove('selected'));

    selectedWord = { card, item };
    card.classList.add('selected');

    if (selectedImage) checkMatch();
  }

  function checkMatch() {
    const imgSel = selectedImage;
    const wrdSel = selectedWord;

    // Reset selections immediately
    selectedImage = null;
    selectedWord = null;

    setTimeout(() => {
      if (imgSel.item.id === wrdSel.item.id) {
        // ✅ CORRECT MATCH
        imgSel.card.classList.remove('selected');
        wrdSel.card.classList.remove('selected');
        imgSel.card.classList.add('matched');
        wrdSel.card.classList.add('matched');

        // Add checkmark overlay
        const check = document.createElement('div');
        check.style.cssText = 'position:absolute;top:4px;right:6px;font-size:1.2rem';
        check.textContent = '✅';
        imgSel.card.appendChild(check);

        // Speak the word
        if ('speechSynthesis' in window) {
          const u = new SpeechSynthesisUtterance(wrdSel.item.word_en);
          u.lang = 'en-US'; u.rate = 0.8;
          speechSynthesis.speak(u);
        }

        score += pointsReward;
        matchedPairs++;
        matchedCountEl.textContent = matchedPairs;
        scoreDisplay.textContent = score;

        if (matchedPairs === totalPairs) {
          // All matched!
          if (timer) timer.stop();
          window.timeSpent = timer ? timer.getElapsed() : 0;
          setTimeout(() => showWinScreen(score, totalPairs * pointsReward, gameId), 600);
        }

      } else {
        // ❌ WRONG MATCH
        imgSel.card.classList.remove('selected');
        wrdSel.card.classList.remove('selected');
        imgSel.card.classList.add('wrong');
        wrdSel.card.classList.add('wrong');
        setTimeout(() => {
          imgSel.card.classList.remove('wrong');
          wrdSel.card.classList.remove('wrong');
        }, 600);
      }
    }, 150);
  }

  // --- Timer ---
  if (timeLimit > 0) {
    const timerEl = document.getElementById('timerDisplay');
    timer = new GameTimer(timeLimit, timerEl, () => {
      window.timeSpent = timeLimit;
      showWinScreen(score, totalPairs * pointsReward, gameId);
    });
    timer.start();
  }
}
