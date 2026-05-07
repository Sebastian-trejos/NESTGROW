"""
Historia mode business logic: achievement verification.
"""
from collections import Counter

from apps.games.models import Logro, LogroUsuario, HuesoTransaccion
from .models import ProgresoLeccion, SeccionHistoria, Leccion

# PKs de los logros del Modo Historia (definidos en logros_historia.json)
_PKS = {
    'primera_leccion':    101,
    'aprendiz':           102,
    'explorador':         103,
    'aventurero':         104,
    'maestro':            105,
    'primera_seccion':    106,
    'mundo_ampliado':     107,
    'gran_viajero':       108,
    'tres_estrellas_1':   109,
    'tres_estrellas_10':  110,
    'estrella_suprema':   111,
    'impecable':          112,
    'racha_diaria':       113,
    'semana_constante':   114,
    'repasador':          115,
    'coleccionista':      116,
    'leyenda':            117,
    'sin_rendirse':       118,
}


def _otorgar(user, logro, logros_nuevos):
    """Award a logro if not already earned. Appends to logros_nuevos list."""
    _, created = LogroUsuario.objects.get_or_create(user=user, logro=logro)
    if created:
        logros_nuevos.append(logro)


def verificar_logros_historia(user, progreso_reciente=None):
    """
    Check and award any Historia achievements the user has earned.

    progreso_reciente — optional ProgresoLeccion just completed, used for
                        fast-path checks (impecable, sin_rendirse).

    Returns a list of newly awarded Logro objects.
    """
    logros_nuevos = []

    # Load all historia logros in one query
    logros_map = {
        lg.pk: lg
        for lg in Logro.objects.filter(pk__in=_PKS.values(), is_active=True)
    }
    if not logros_map:
        return logros_nuevos  # fixture not loaded yet

    # Already-earned historia logro PKs for this user
    ya_ganados = set(
        LogroUsuario.objects
        .filter(user=user, logro__pk__in=_PKS.values())
        .values_list('logro_id', flat=True)
    )

    def _pendiente(clave):
        pk = _PKS.get(clave)
        return pk and pk not in ya_ganados and pk in logros_map

    def _award(clave):
        pk = _PKS[clave]
        _otorgar(user, logros_map[pk], logros_nuevos)

    # ── Datos base ────────────────────────────────────────────────────────────
    progresos = ProgresoLeccion.objects.filter(estudiante=user, completada=True)
    completadas_count  = progresos.count()
    triple_estrella    = progresos.filter(estrellas=3).count()

    # Estrellas totales desde el perfil (ya actualizado antes de llamar aquí)
    try:
        total_estrellas = user.estudiante_profile.total_estrellas_historia
    except Exception:
        total_estrellas = progresos.aggregate(
            s=__import__('django.db.models', fromlist=['Sum']).Sum('estrellas')
        )['s'] or 0

    # ── Logros por cantidad de lecciones ─────────────────────────────────────
    if _pendiente('primera_leccion') and completadas_count >= 1:
        _award('primera_leccion')
    if _pendiente('aprendiz') and completadas_count >= 5:
        _award('aprendiz')
    if _pendiente('explorador') and completadas_count >= 10:
        _award('explorador')
    if _pendiente('aventurero') and completadas_count >= 25:
        _award('aventurero')
    if _pendiente('maestro') and completadas_count >= 52:
        _award('maestro')

    # ── Logros por secciones completas ───────────────────────────────────────
    if any(_pendiente(k) for k in ('primera_seccion', 'mundo_ampliado', 'gran_viajero')):
        secciones_completas = _contar_secciones_completas(user)
        if _pendiente('primera_seccion') and secciones_completas >= 1:
            _award('primera_seccion')
        if _pendiente('mundo_ampliado') and secciones_completas >= 5:
            _award('mundo_ampliado')
        if _pendiente('gran_viajero') and secciones_completas >= 10:
            _award('gran_viajero')

    # ── Logros por estrellas ──────────────────────────────────────────────────
    if _pendiente('tres_estrellas_1') and triple_estrella >= 1:
        _award('tres_estrellas_1')
    if _pendiente('tres_estrellas_10') and triple_estrella >= 10:
        _award('tres_estrellas_10')
    if _pendiente('estrella_suprema') and triple_estrella >= 52:
        _award('estrella_suprema')

    if _pendiente('coleccionista') and total_estrellas >= 50:
        _award('coleccionista')
    if _pendiente('leyenda') and total_estrellas >= 100:
        _award('leyenda')

    # ── Logros de lección específica (usan progreso_reciente) ─────────────────
    if progreso_reciente:
        if _pendiente('impecable') and progreso_reciente.intentos == 1 and progreso_reciente.estrellas == 3:
            _award('impecable')
        if _pendiente('sin_rendirse') and progreso_reciente.intentos >= 3 and progreso_reciente.completada:
            _award('sin_rendirse')

    # ── Racha diaria (3 lecciones en un mismo día) ────────────────────────────
    if _pendiente('racha_diaria'):
        fechas = progresos.values_list('completada_en', flat=True)
        dias = Counter(f.date() for f in fechas if f)
        if any(v >= 3 for v in dias.values()):
            _award('racha_diaria')

    # ── Semana constante (7 días distintos con al menos 1 lección) ────────────
    if _pendiente('semana_constante'):
        fechas = progresos.values_list('completada_en', flat=True)
        dias_unicos = {f.date() for f in fechas if f}
        if len(dias_unicos) >= 7:
            _award('semana_constante')

    # ── Repasador (3⭐ en todas las lecciones de repaso) ──────────────────────
    if _pendiente('repasador'):
        total_repaso = Leccion.objects.filter(titulo__icontains='repaso').count()
        if total_repaso > 0:
            repaso_3_stars = progresos.filter(
                leccion__titulo__icontains='repaso',
                estrellas=3,
            ).count()
            if repaso_3_stars >= total_repaso:
                _award('repasador')

    return logros_nuevos


def _contar_secciones_completas(user):
    """Return how many SeccionHistoria the user has fully completed."""
    secciones = SeccionHistoria.objects.prefetch_related('lecciones').all()
    count = 0
    completadas_ids = set(
        ProgresoLeccion.objects
        .filter(estudiante=user, completada=True)
        .values_list('leccion_id', flat=True)
    )
    for sec in secciones:
        lec_ids = set(sec.lecciones.values_list('pk', flat=True))
        if lec_ids and lec_ids.issubset(completadas_ids):
            count += 1
    return count
