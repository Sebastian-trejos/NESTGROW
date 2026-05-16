// NESTGROW - Score Toast Utility
// Muestra notificaciones flotantes "+X" o "-X" al lado del marcador

(function () {
  if (!document.getElementById('scoreToastStyle')) {
    const style = document.createElement('style');
    style.id = 'scoreToastStyle';
    style.textContent = `
      @keyframes scoreToastRise {
        0%   { opacity: 1; transform: translateX(-50%) translateY(0) scale(1.1); }
        60%  { opacity: 1; }
        100% { opacity: 0; transform: translateX(-50%) translateY(-70px) scale(0.9); }
      }
      .score-toast-el {
        position: fixed;
        left: 50%;
        bottom: 22%;
        transform: translateX(-50%);
        font-size: 1.8rem;
        font-weight: 900;
        pointer-events: none;
        z-index: 9999;
        font-family: 'Fredoka One', cursive;
        letter-spacing: 0.03em;
        text-shadow: 0 2px 8px rgba(0,0,0,0.25);
        animation: scoreToastRise 0.85s ease-out forwards;
      }
    `;
    document.head.appendChild(style);
  }
})();

function showScoreToast(amount, isPositive) {
  const el = document.createElement('div');
  el.className = 'score-toast-el';
  el.textContent = (isPositive ? '+' : '-') + amount;
  el.style.color = isPositive ? '#4CAF50' : '#e53935';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 860);
}
