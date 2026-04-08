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
    setTimeout(() => { miloVisible = false; bubble.classList.remove('show'); }, 5000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const bubble = document.getElementById('miloBubble');
  if (bubble) {
    setTimeout(() => {
      bubble.classList.add('show'); miloVisible = true;
      setTimeout(() => { bubble.classList.remove('show'); miloVisible = false; }, 4000);
    }, 1500);
  }

  // Animate cards
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('fade-in-up'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.nestgrow-card, .game-card, .stat-card').forEach(el => observer.observe(el));

  // Show badge popup if pending
  showPendingBadgePopup();
});

// --- CSRF ---
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}

// --- Save Score ---
async function saveScore(gameId, score, maxScore, timeSpent, completed = false) {
  try {
    const response = await fetch('/juegos/guardar-puntaje/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify({ game_id: gameId, score, max_score: maxScore, time_spent: timeSpent, completed }),
    });
    return await response.json();
  } catch (err) {
    console.error('Error saving score:', err);
    return null;
  }
}

// --- Win Screen with Classification ---
async function showWinScreen(score, maxScore, gameId) {
  const overlay = document.getElementById('winOverlay');
  if (!overlay) return;

  const pct = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;

  // Classification
  let clasif, clasifColor, stars;
  if (pct >= 90)      { clasif = '🏆 ¡Perfecto!';           clasifColor = '#4CAF50'; stars = '⭐⭐⭐'; }
  else if (pct >= 70) { clasif = '⭐ ¡Alto!';               clasifColor = '#6C63FF'; stars = '⭐⭐⭐'; }
  else if (pct >= 50) { clasif = '👍 Básico';               clasifColor = '#FFB347'; stars = '⭐⭐'; }
  else                { clasif = '💪 ¡Sigue practicando!';  clasifColor = '#FF6B6B'; stars = '⭐'; }

  // Update overlay elements
  if (document.getElementById('winScore'))   document.getElementById('winScore').textContent = score;
  if (document.getElementById('winPercent')) document.getElementById('winPercent').textContent = pct + '%';
  if (document.getElementById('winStars'))   document.getElementById('winStars').textContent = stars;
  if (document.getElementById('winClasif')) {
    document.getElementById('winClasif').textContent = clasif;
    document.getElementById('winClasif').style.color = clasifColor;
  }

  overlay.style.display = 'flex';
  launchConfetti();

  // Save and handle rewards
  const result = await saveScore(gameId, score, maxScore, window.timeSpent || 0, true);
  if (result) {
    // Show huesos earned
    if (result.huesos_ganados && document.getElementById('winHuesos')) {
      document.getElementById('winHuesos').textContent = `+${result.huesos_ganados} 🦴 Huesos de Milo`;
    }
    // Show level up popup
    if (result.subio_nivel) {
      setTimeout(() => showLevelUpPopup(result.nuevo_nivel), 1000);
    }
    // Show new badges
    if (result.nuevos_logros && result.nuevos_logros.length > 0) {
      const delay = result.subio_nivel ? 4000 : 1500;
      setTimeout(() => showBadgePopup(result.nuevos_logros[0]), delay);
    }
  }
}

// --- Level Up Popup ---
function showLevelUpPopup(nivel) {
  document.getElementById('levelUpPopup')?.remove();
  document.getElementById('levelUpBackdrop')?.remove();

  const backdrop = document.createElement('div');
  backdrop.id = 'levelUpBackdrop';
  backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:99998';

  const popup = document.createElement('div');
  popup.id = 'levelUpPopup';
  popup.style.cssText = `
    position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(0);
    background:linear-gradient(135deg,#6C63FF,#9c94ff);
    border-radius:28px;padding:40px 50px;text-align:center;
    box-shadow:0 20px 60px rgba(108,99,255,0.5);z-index:99999;
    animation:badgePop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) forwards;
    max-width:380px;width:90%;color:white;
  `;
  popup.innerHTML = `
    <div style="font-size:5rem;animation:bobble 1s infinite">🐺</div>
    <div style="font-size:0.9rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-top:8px;opacity:0.85">
      ¡Subiste de Nivel!
    </div>
    <div style="font-family:'Fredoka One',cursive;font-size:3.5rem;margin:8px 0;line-height:1">
      Nivel ${nivel}
    </div>
    <div style="font-weight:700;font-size:1rem;opacity:0.9;margin-bottom:16px">
      ¡Milo te da 15 🦴 Huesos de Milo como recompensa!
    </div>
    <div style="background:rgba(255,255,255,0.2);border-radius:16px;padding:10px 20px;font-size:1.8rem;letter-spacing:4px">
      🦴🦴🦴
    </div>
    <button onclick="this.closest('#levelUpPopup').remove();document.getElementById('levelUpBackdrop').remove();"
      style="margin-top:20px;background:white;color:#6C63FF;border:none;
             border-radius:50px;padding:10px 30px;font-family:'Fredoka One',cursive;
             font-size:1.1rem;cursor:pointer">
      ¡Genial! 🎉
    </button>
  `;

  backdrop.onclick = () => { popup.remove(); backdrop.remove(); };
  document.body.appendChild(backdrop);
  document.body.appendChild(popup);
  launchConfetti();
  setTimeout(() => { popup.remove(); backdrop.remove(); }, 7000);
}

// --- Badge Popup ---
function showBadgePopup(logro) {
  // Remove existing
  document.getElementById('badgePopup')?.remove();

  const popup = document.createElement('div');
  popup.id = 'badgePopup';
  popup.style.cssText = `
    position:fixed; top:50%; left:50%; transform:translate(-50%,-50%) scale(0);
    background:white; border-radius:28px; padding:40px 50px; text-align:center;
    box-shadow:0 20px 60px rgba(108,99,255,0.35); z-index:99999;
    animation:badgePop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) forwards;
    max-width:380px; width:90%;
  `;
  popup.innerHTML = `
    <div style="font-size:5rem;animation:bobble 1s infinite">${logro.icono}</div>
    <div style="font-size:0.9rem;font-weight:700;color:#6C63FF;text-transform:uppercase;letter-spacing:2px;margin-top:8px">
      🎉 ¡Nuevo Logro!
    </div>
    <div style="font-family:'Fredoka One',cursive;font-size:1.8rem;color:#2D2D2D;margin:8px 0">${logro.nombre}</div>
    <div style="color:#666;font-weight:700;font-size:0.95rem">${logro.descripcion}</div>
    <button onclick="this.closest('#badgePopup').remove()"
      style="margin-top:20px;background:linear-gradient(135deg,#6C63FF,#9c94ff);color:white;border:none;
             border-radius:50px;padding:10px 30px;font-family:'Fredoka One',cursive;font-size:1.1rem;cursor:pointer">
      ¡Genial! 🎊
    </button>
  `;

  // Backdrop
  const backdrop = document.createElement('div');
  backdrop.id = 'badgeBackdrop';
  backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:99998';
  backdrop.onclick = () => { popup.remove(); backdrop.remove(); };

  document.body.appendChild(backdrop);
  document.body.appendChild(popup);

  // Inject keyframe
  if (!document.getElementById('badgePopKeyframe')) {
    const s = document.createElement('style');
    s.id = 'badgePopKeyframe';
    s.textContent = '@keyframes badgePop{from{transform:translate(-50%,-50%) scale(0);opacity:0}to{transform:translate(-50%,-50%) scale(1);opacity:1}}';
    document.head.appendChild(s);
  }

  // Auto-close after 6s
  setTimeout(() => { popup.remove(); backdrop.remove(); }, 6000);

  // Mark as seen via AJAX
  fetch('/juegos/logro-visto/', {
    method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() }
  });
}

// Show pending badges (on page load)
async function showPendingBadgePopup() {
  const pendingEl = document.getElementById('pendingBadges');
  if (!pendingEl) return;
  try {
    const badges = JSON.parse(pendingEl.dataset.badges || '[]');
    if (badges.length > 0) {
      setTimeout(() => showBadgePopup(badges[0]), 2000);
    }
  } catch(e) {}
}

// --- Confetti ---
function launchConfetti() {
  const colors = ['#6C63FF','#FF6B6B','#4ECDC4','#FFE66D','#A8E6CF'];
  for (let i = 0; i < 80; i++) {
    const el = document.createElement('div');
    el.style.cssText = `position:fixed;left:${Math.random()*100}vw;top:-10px;
      width:${Math.random()*10+5}px;height:${Math.random()*10+5}px;
      background:${colors[Math.floor(Math.random()*colors.length)]};
      border-radius:${Math.random()>0.5?'50%':'2px'};
      animation:confettiFall ${Math.random()*2+2}s linear forwards;z-index:99999;`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }
}
const s = document.createElement('style');
s.textContent = '@keyframes confettiFall{to{transform:translateY(110vh) rotate(720deg);opacity:0}}';
document.head.appendChild(s);

// --- Timer ---
class GameTimer {
  constructor(seconds, displayEl, onEnd) {
    this.total = seconds; this.remaining = seconds;
    this.display = displayEl; this.onEnd = onEnd; this.interval = null;
  }
  start() {
    this.interval = setInterval(() => {
      this.remaining--;
      if (this.display) {
        const m = Math.floor(this.remaining/60).toString().padStart(2,'0');
        const s = (this.remaining%60).toString().padStart(2,'0');
        this.display.textContent = `${m}:${s}`;
        if (this.remaining <= 10) this.display.style.color = '#FF6B6B';
      }
      if (this.remaining <= 0) { clearInterval(this.interval); if (this.onEnd) this.onEnd(); }
    }, 1000);
  }
  stop() { clearInterval(this.interval); }
  getElapsed() { return this.total - this.remaining; }
}
