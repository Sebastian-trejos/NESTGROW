// ============================================================
// NESTGROW - Main JavaScript
// ============================================================

// --- Milo Mascot ---
let miloVisible = false;

function toggleMiloMessage() {
  const bubble = document.getElementById('miloBubble');
  if (!bubble) return;
  miloVisible = !miloVisible;
  bubble.classList.toggle('show', miloVisible);
  if (miloVisible) {
    setTimeout(() => {
      miloVisible = false;
      bubble.classList.remove('show');
    }, 5000);
  }
}

// Auto-show Milo on page load for first visit
document.addEventListener('DOMContentLoaded', () => {
  const bubble = document.getElementById('miloBubble');
  if (bubble) {
    setTimeout(() => {
      bubble.classList.add('show');
      miloVisible = true;
      setTimeout(() => {
        bubble.classList.remove('show');
        miloVisible = false;
      }, 4000);
    }, 1500);
  }

  // Animate cards on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.nestgrow-card, .game-card, .stat-card').forEach(el => {
    observer.observe(el);
  });
});

// --- CSRF Helper for AJAX ---
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}

// --- Save Score to Server ---
async function saveScore(gameId, score, timeSpent, completed = false) {
  try {
    const response = await fetch('/juegos/guardar-puntaje/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ game_id: gameId, score, time_spent: timeSpent, completed }),
    });
    return await response.json();
  } catch (err) {
    console.error('Error saving score:', err);
  }
}

// --- Show Win Overlay ---
function showWinScreen(score, maxScore, gameId) {
  const overlay = document.getElementById('winOverlay');
  if (!overlay) return;
  const pct = Math.round((score / maxScore) * 100);
  document.getElementById('winScore').textContent = score;
  document.getElementById('winPercent').textContent = pct + '%';
  // Stars
  let stars = pct >= 90 ? '⭐⭐⭐' : pct >= 60 ? '⭐⭐' : '⭐';
  document.getElementById('winStars').textContent = stars;
  overlay.style.display = 'flex';
  // Confetti
  launchConfetti();
  saveScore(gameId, score, window.timeSpent || 0, true);
}

// --- Simple Confetti ---
function launchConfetti() {
  const colors = ['#6C63FF', '#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF'];
  for (let i = 0; i < 80; i++) {
    const el = document.createElement('div');
    el.style.cssText = `
      position: fixed;
      left: ${Math.random() * 100}vw;
      top: -10px;
      width: ${Math.random() * 10 + 5}px;
      height: ${Math.random() * 10 + 5}px;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
      animation: confettiFall ${Math.random() * 2 + 2}s linear forwards;
      z-index: 99999;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }
}

// Inject confetti keyframes
const style = document.createElement('style');
style.textContent = `
@keyframes confettiFall {
  to { transform: translateY(110vh) rotate(720deg); opacity: 0; }
}`;
document.head.appendChild(style);

// --- Timer ---
class GameTimer {
  constructor(seconds, displayEl, onEnd) {
    this.total = seconds;
    this.remaining = seconds;
    this.display = displayEl;
    this.onEnd = onEnd;
    this.interval = null;
  }
  start() {
    this.interval = setInterval(() => {
      this.remaining--;
      if (this.display) {
        const m = Math.floor(this.remaining / 60).toString().padStart(2, '0');
        const s = (this.remaining % 60).toString().padStart(2, '0');
        this.display.textContent = `${m}:${s}`;
        if (this.remaining <= 10) this.display.style.color = '#FF6B6B';
      }
      if (this.remaining <= 0) {
        clearInterval(this.interval);
        if (this.onEnd) this.onEnd();
      }
    }, 1000);
  }
  stop() { clearInterval(this.interval); }
  getElapsed() { return this.total - this.remaining; }
}
