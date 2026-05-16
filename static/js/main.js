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

// --- Result Screen with Milo images and varied messages ---
const MILO_IMG = {
  excelente: ['img/milo_fest.png','img/milo_fest2.png','img/milo_orgulloso.png','img/milo_asombrado.png','img/milo_bai.png','img/milo_star.png','img/milo_saludando.png'],
  bien:      ['img/milo_saludando.png','img/milo_hablando.png','img/milo_orgulloso.png','img/milo_asombrado2.png','img/milo_fest.png'],
  regular:   ['img/milo_lupa1.png','img/milo_lupa2.png','img/milo_duda1.png','img/milo_duda2.png','img/milo_interroga.png','img/milo_preocupado.png','img/milo_hablando.png'],
  mal:       ['img/milo_llorando.png','img/milo_lagri.png','img/milo_enojado2.png','img/milo_enojado1.png','img/milo_preocupado.png']
};
const MSG_TIER = {
  excelente: ['¡Perfecto!','¡Excelente trabajo!','¡Eres un genio!','¡Impresionante!','¡Fuera de serie!'],
  bien:      ['¡Muy bien hecho!','¡Buen trabajo!','¡Lo estás haciendo genial!','¡Sigue brillando!','¡Buenísimo!'],
  regular:   ['¡Bien! Puedes mejorar.','¡Sigue practicando!','¡Vas por buen camino!','¡Casi lo logras!','¡Un poco más!'],
  mal:       ['¡Sigue intentando! Tú puedes.','¡No te rindas!','¡La práctica hace al maestro!','¡Cada intento cuenta!','¡Ánimo! La próxima será mejor.','¡Tú puedes!']
};

function pickRand(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

async function showWinScreen(score, maxScore, gameId) {
  const overlay = document.getElementById('winOverlay');
  if (!overlay) return;

  const pct = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;

  let tier, clasif, stars, miloFile, msg, clasifColor;
  if (pct >= 90)      { tier='excelente'; clasif='¡Perfecto!';   clasifColor='#4CAF50'; stars='⭐⭐⭐'; }
  else if (pct >= 70) { tier='bien';      clasif='¡Muy bien!';   clasifColor='#6C63FF'; stars='⭐⭐⭐'; }
  else if (pct >= 50) { tier='regular';   clasif='Buen intento'; clasifColor='#FFB347'; stars='⭐⭐'; }
  else                { tier='mal';        clasif='Sigue practicando'; clasifColor='#FF6B6B'; stars='⭐'; }

  miloFile = pickRand(MILO_IMG[tier]);
  msg = pickRand(MSG_TIER[tier]);

  const $ = id => document.getElementById(id);

  if ($('winMilo')) $('winMilo').src = STATIC_URL + miloFile;
  if ($('winMessage')) $('winMessage').textContent = msg;
  if ($('winStars')) $('winStars').textContent = stars;
  if ($('winScore')) $('winScore').textContent = score;
  if ($('winPercent')) $('winPercent').textContent = pct + '%';
  if ($('winClasif')) {
    $('winClasif').textContent = clasif;
    $('winClasif').style.color = clasifColor;
  }

  const card = overlay.querySelector('.win-card');
  if (card) {
    card.className = 'win-card';
    card.classList.add('win-card--' + tier);
  }

  overlay.style.display = 'flex';

  if (tier === 'excelente' || tier === 'bien') launchConfetti();

  const result = await saveScore(gameId, score, maxScore, window.timeSpent || 0, true);
  if (result) {
    if (result.huesos_ganados && $('winHuesos')) {
      $('winHuesos').textContent = `+${result.huesos_ganados} 🦴 Huesos de Milo`;
    }
    if (result.registro_pk && $('btnVolverPanel')) {
      $('btnVolverPanel').href = '/talleres/mis-talleres/?revisado=' + result.registro_pk;
    }
    if (result.subio_nivel) setTimeout(() => showLevelUpPopup(result.nuevo_nivel), 1000);
    if (result.nuevos_logros && result.nuevos_logros.length > 0) {
      setTimeout(() => showBadgePopup(result.nuevos_logros[0]), result.subio_nivel ? 4000 : 1500);
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
