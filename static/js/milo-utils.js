// NestGrow — Utilidades globales de Milo
// Requiere canvas-confetti cargado en base.html (window.confetti)

function launchConfetti(opts) {
  if (typeof confetti !== 'function') return;
  confetti(Object.assign({
    particleCount: 120,
    spread: 90,
    origin: { y: 0.6 },
    colors: ['#6C63FF', '#FF6B6B', '#4ECDC4', '#FFE66D', '#FFB347', '#A8E6CF'],
  }, opts || {}));
}

function lanzarConfetiFuerte() {
  if (typeof confetti !== 'function') return;
  const colors = ['#6C63FF', '#FF6B6B', '#4ECDC4', '#FFE66D', '#FFB347'];
  confetti({ particleCount: 150, spread: 120, origin: { y: 0.5 }, colors });
  setTimeout(() => confetti({ particleCount: 80, angle: 60, spread: 80, origin: { x: 0, y: 0.6 }, colors }), 350);
  setTimeout(() => confetti({ particleCount: 80, angle: 120, spread: 80, origin: { x: 1, y: 0.6 }, colors }), 700);
}
