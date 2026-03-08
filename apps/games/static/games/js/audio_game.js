// ============================================================
// NESTGROW - Audio Matching Game
// ============================================================

function initAudioGame(vocabulary, gameId, pointsReward) {
  if (vocabulary.length === 0) return;

  const items = [...vocabulary].sort(() => Math.random() - 0.5).slice(0, 6);
  let currentIndex = 0;
  let score = 0;
  let answered = false;

  const scoreDisplay = document.getElementById('scoreDisplay');
  const roundDisplay = document.getElementById('roundDisplay');
  const totalRoundsEl = document.getElementById('totalRounds');
  const optionsGrid = document.getElementById('optionsGrid');
  const playBtn = document.getElementById('playAudioBtn');
  const audioHint = document.getElementById('audioHint');

  totalRoundsEl.textContent = items.length;

  function shuffle(arr) { return [...arr].sort(() => Math.random() - 0.5); }

  function speakWord(word) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(word);
      u.lang = 'en-US';
      u.rate = 0.75;
      u.pitch = 1.1;
      window.speechSynthesis.speak(u);
    }
  }

  function playCurrentAudio() {
    const item = items[currentIndex];
    if (item.audio) {
      const audio = new Audio(item.audio);
      audio.play();
    } else {
      speakWord(item.word_en);
    }
    playBtn.style.transform = 'scale(1.2)';
    setTimeout(() => playBtn.style.transform = '', 300);
  }

  function loadRound() {
    if (currentIndex >= items.length) {
      endGame();
      return;
    }
    answered = false;
    roundDisplay.textContent = currentIndex + 1;
    optionsGrid.innerHTML = '';
    audioHint.textContent = 'Press to hear the word! / ¡Presiona para escuchar!';

    const correct = items[currentIndex];
    // Pick 3 wrong options from remaining items
    const wrongPool = items.filter((_, i) => i !== currentIndex);
    const wrongs = shuffle(wrongPool).slice(0, 3);
    const options = shuffle([correct, ...wrongs]);

    options.forEach(item => {
      const col = document.createElement('div');
      col.className = 'col-6 col-md-3';
      col.innerHTML = `
        <div class="option-card nestgrow-card p-3 text-center" data-id="${item.id}" style="cursor:pointer">
          ${item.image
            ? `<img src="${item.image}" alt="${item.word_en}" class="rounded-3 mb-2" style="width:100%;height:90px;object-fit:cover">`
            : `<div class="mb-2" style="font-size:2.5rem;height:80px;display:flex;align-items:center;justify-content:center;background:#f0eeff;border-radius:12px">${item.word_en[0]}</div>`
          }
          <div class="fw-bold" style="font-size:0.9rem;color:var(--primary)">${item.word_en}</div>
        </div>`;

      col.querySelector('.option-card').addEventListener('click', () => checkAnswer(item, correct));
      optionsGrid.appendChild(col);
    });

    // Auto-play
    setTimeout(playCurrentAudio, 500);
  }

  function checkAnswer(selected, correct) {
    if (answered) return;
    answered = true;

    const cards = optionsGrid.querySelectorAll('.option-card');
    cards.forEach(card => {
      card.style.pointerEvents = 'none';
      const id = parseInt(card.dataset.id);
      if (id === correct.id) {
        card.style.border = '3px solid #4caf50';
        card.style.background = '#e8f5e9';
      } else if (id === selected.id && id !== correct.id) {
        card.style.border = '3px solid var(--secondary)';
        card.style.background = '#ffe8e8';
      }
    });

    if (selected.id === correct.id) {
      score += pointsReward;
      scoreDisplay.textContent = score;
      audioHint.textContent = `✅ Correct! "${correct.word_en}" = ${correct.word_es}`;
      speakWord('Correct!');
    } else {
      audioHint.textContent = `❌ The answer was "${correct.word_en}" / La respuesta era "${correct.word_en}"`;
    }

    setTimeout(() => {
      currentIndex++;
      loadRound();
    }, 1800);
  }

  function endGame() {
    window.timeSpent = 0;
    showWinScreen(score, items.length * pointsReward, gameId);
  }

  playBtn.addEventListener('click', playCurrentAudio);
  loadRound();
}
