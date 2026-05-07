import io
import json
from PIL import Image, ImageDraw

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db import models as db_models

from .models import (
    SeccionHistoria, SeccionDesbloqueada, Leccion,
    ActividadLeccion, ProgresoLeccion, RespuestaActividad,
)
from apps.accounts.decorators import profesor_required, estudiante_required
from apps.games.models import HuesoTransaccion

# ── Placeholder image helpers ─────────────────────────────────────────────────

_COLOR_MAP = [
    (['color', 'rojo', 'red', 'azul', 'blue', 'verde', 'green'], '#FF6B6B'),
    (['familia', 'family', 'papa', 'mama', 'hermano'],            '#FF9F43'),
    (['numero', 'number', 'math', 'count'],                        '#FECA57'),
    (['animal', 'lion', 'dog', 'cat', 'fish'],                     '#48DBFB'),
    (['cuerpo', 'body', 'head', 'hand', 'foot'],                   '#FF9FF3'),
    (['comida', 'food', 'fruit', 'apple', 'banana'],               '#54A0FF'),
    (['casa', 'house', 'home', 'room', 'bed'],                     '#5F27CD'),
    (['tiempo', 'weather', 'rain', 'sun', 'season'],               '#00D2D3'),
    (['deporte', 'sport', 'hobby', 'dance', 'music'],              '#FF9F43'),
    (['pueblo', 'town', 'city', 'school', 'bus'],                  '#6C63FF'),
]
_DEFAULT_COLOR = '#6C63FF'


def _pick_color(nombre: str) -> str:
    slug = nombre.lower().replace('_', ' ')
    for keywords, color in _COLOR_MAP:
        if any(k in slug for k in keywords):
            return color
    return _DEFAULT_COLOR


def placeholder_img(request, nombre):
    """Generate a 400×300 PNG placeholder for historia activity images."""
    bg_hex = _pick_color(nombre)
    bg_rgb = tuple(int(bg_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    dark   = tuple(max(0, c - 40) for c in bg_rgb)

    img  = Image.new('RGB', (400, 300), color=bg_rgb)
    draw = ImageDraw.Draw(img)
    draw.ellipse([300, -40, 460, 120], fill=dark)
    draw.ellipse([-60, 200, 100, 360], fill=dark)
    label = nombre.replace('_', ' ').replace('-', ' ').title()
    draw.text((200, 150), label, fill='white', anchor='mm')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')


# ── Shared helpers ────────────────────────────────────────────────────────────

def _seccion_desbloqueada(seccion, estudiante):
    """Return True if seccion is accessible for this EstudianteProfile."""
    if seccion.is_desbloqueada_por_defecto:
        return True
    if not estudiante.salon:
        return False
    return SeccionDesbloqueada.objects.filter(
        seccion=seccion, salon=estudiante.salon
    ).exists()


def _evaluar_respuesta(actividad, respuesta_dada):
    """
    Evaluate a submitted answer for an activity.
    Returns (es_correcta: bool|None, respuesta_correcta_display: str)
    None means no grading (intro, vocab, dialogo).
    """
    tipo  = actividad.tipo
    datos = actividad.datos

    if tipo == 'listening':
        preguntas = datos.get('preguntas', [])
        resps     = respuesta_dada.get('respuestas', [])
        if not preguntas:
            return True, ''
        correctas = sum(
            1 for i, p in enumerate(preguntas)
            if i < len(resps) and resps[i] == p['respuesta_correcta']
        )
        return (correctas / len(preguntas)) >= 0.7, ''

    if tipo == 'reading':
        preguntas = datos.get('preguntas', [])
        resps     = respuesta_dada.get('respuestas', [])
        if not preguntas:
            return True, ''
        correctas = sum(
            1 for i, p in enumerate(preguntas)
            if i < len(resps) and resps[i] == p['respuesta_correcta']
        )
        return (correctas / len(preguntas)) >= 0.7, ''

    if tipo == 'writing':
        ejercicios = datos.get('ejercicios', [])
        resps      = respuesta_dada.get('respuestas', [])
        if not ejercicios:
            return True, ''
        correctas = sum(
            1 for i, e in enumerate(ejercicios)
            if i < len(resps) and resps[i].strip().lower() == e['en'].lower()
        )
        return (correctas / len(ejercicios)) >= 0.7, ''

    if tipo in ('pronunciacion', 'minijuego_embed'):
        return True, ''

    return None, ''   # intro, vocabulario, dialogo — no grading


# ── Estudiante: mapa ──────────────────────────────────────────────────────────

@login_required
def mapa_historia(request):
    if request.user.is_profesor():
        return redirect('historia:panel_historia_profesor')

    try:
        estudiante = request.user.estudiante_profile
    except Exception:
        return redirect('accounts:dashboard')

    secciones_qs = SeccionHistoria.objects.prefetch_related('lecciones').order_by('orden')

    # Collect all ProgresoLeccion for this student in one query
    todos_progresos = {
        p.leccion_id: p
        for p in ProgresoLeccion.objects.filter(estudiante=request.user)
    }

    secciones_data = []
    primera_incompleta = None   # (seccion_pk, leccion_pk) for "continue" button

    for seccion in secciones_qs:
        desbloqueada = _seccion_desbloqueada(seccion, estudiante)
        lecciones    = list(seccion.lecciones.order_by('orden'))
        total        = len(lecciones)
        completadas  = 0
        estrellas    = 0
        lecciones_data = []

        prev_completada = True   # first lesson always accessible within unlocked section
        for lec in lecciones:
            prog = todos_progresos.get(lec.pk)
            lec_completada = prog.completada if prog else False
            lec_estrellas  = prog.estrellas  if prog else 0
            accesible      = desbloqueada and prev_completada

            if lec_completada:
                completadas += 1
                estrellas   += lec_estrellas
            elif accesible and primera_incompleta is None:
                primera_incompleta = (seccion.pk, lec.pk)

            lecciones_data.append({
                'leccion':    lec,
                'progreso':   prog,
                'completada': lec_completada,
                'estrellas':  lec_estrellas,
                'accesible':  accesible,
            })
            prev_completada = lec_completada

        secciones_data.append({
            'seccion':       seccion,
            'desbloqueada':  desbloqueada,
            'lecciones':     lecciones_data,
            'completadas':   completadas,
            'total':         total,
            'estrellas':     estrellas,
            'max_estrellas': total * 3,
            'completa':      desbloqueada and completadas == total and total > 0,
        })

    try:
        total_estrellas = request.user.estudiante_profile.total_estrellas_historia
    except Exception:
        total_estrellas = 0

    return render(request, 'historia/mapa.html', {
        'secciones_data':    secciones_data,
        'primera_incompleta': primera_incompleta,
        'total_estrellas':   total_estrellas,
    })


# ── Estudiante: ver lección ───────────────────────────────────────────────────

@login_required
@estudiante_required
def ver_leccion(request, pk):
    leccion = get_object_or_404(Leccion, pk=pk)
    seccion = leccion.seccion

    try:
        estudiante = request.user.estudiante_profile
    except Exception:
        return redirect('accounts:dashboard')

    if not _seccion_desbloqueada(seccion, estudiante):
        messages.error(request, '🔒 Esta sección aún no está desbloqueada.')
        return redirect('historia:mapa_historia')

    actividades = list(leccion.actividades.order_by('orden'))

    progreso, created = ProgresoLeccion.objects.get_or_create(
        estudiante=request.user,
        leccion=leccion,
        defaults={'intentos': 1, 'actividad_actual': 0},
    )

    # New attempt: if just created OR restarting a completed lesson
    if not created:
        if progreso.completada:
            # Retry: reset progress
            progreso.completada      = False
            progreso.actividad_actual = 0
            progreso.puntos_obtenidos = 0
            progreso.intentos        += 1
            progreso.save(update_fields=[
                'completada', 'actividad_actual', 'puntos_obtenidos', 'intentos'
            ])
            # Clear previous answers for a clean retry
            RespuestaActividad.objects.filter(progreso=progreso).delete()
        elif created is False and progreso.actividad_actual == 0 and progreso.intentos == 0:
            progreso.intentos = 1
            progreso.save(update_fields=['intentos'])

    actividades_json = json.dumps([
        {
            'pk':             a.pk,
            'orden':          a.orden,
            'tipo':           a.tipo,
            'datos':          a.datos,
            'puntos':         a.puntos_actividad,
            'tiene_correcta': a.tiene_respuesta_correcta(),
        }
        for a in actividades
    ], ensure_ascii=False)

    return render(request, 'historia/leccion.html', {
        'leccion':          leccion,
        'seccion':          seccion,
        'actividades_json': actividades_json,
        'total_actividades': len(actividades),
        'actividad_inicial': progreso.actividad_actual,
        'progreso':         progreso,
    })


# ── AJAX: guardar respuesta ───────────────────────────────────────────────────

@login_required
@require_POST
def guardar_respuesta(request):
    try:
        data          = json.loads(request.body)
        leccion_pk    = data.get('leccion_pk')
        actividad_pk  = data.get('actividad_pk')
        respuesta_dada = data.get('respuesta_dada', {})

        leccion   = get_object_or_404(Leccion, pk=leccion_pk)
        actividad = get_object_or_404(ActividadLeccion, pk=actividad_pk, leccion=leccion)

        progreso, _ = ProgresoLeccion.objects.get_or_create(
            estudiante=request.user,
            leccion=leccion,
        )

        es_correcta, _ = _evaluar_respuesta(actividad, respuesta_dada)

        RespuestaActividad.objects.update_or_create(
            progreso=progreso,
            actividad=actividad,
            defaults={
                'respuesta_dada': respuesta_dada,
                'es_correcta':    es_correcta,
            },
        )

        # Award points (only on first correct submission per activity)
        puntos = 0
        if es_correcta and actividad.puntos_actividad > 0:
            already_awarded = progreso.actividad_actual > (actividad.orden - 1)
            if not already_awarded:
                puntos = actividad.puntos_actividad
                progreso.puntos_obtenidos = db_models.F('puntos_obtenidos') + puntos

        # Advance actividad_actual (idempotent — never go backwards)
        nueva_pos = actividad.orden   # 1-based, after submitting orden=N → pos becomes N
        update_fields = ['puntos_obtenidos']
        if progreso.actividad_actual < nueva_pos:
            progreso.actividad_actual = nueva_pos
            update_fields.append('actividad_actual')
        progreso.save(update_fields=update_fields)
        progreso.refresh_from_db()

        total_acts   = leccion.actividades.count()
        es_ultima    = progreso.actividad_actual >= total_acts

        return JsonResponse({
            'status':              'ok',
            'es_correcta':         es_correcta,
            'puntos':              puntos,
            'es_ultima_actividad': es_ultima,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ── AJAX: completar lección ───────────────────────────────────────────────────

@login_required
@require_POST
def completar_leccion(request, pk):
    try:
        leccion  = get_object_or_404(Leccion, pk=pk)
        progreso = get_object_or_404(ProgresoLeccion, estudiante=request.user, leccion=leccion)

        if progreso.completada:
            return JsonResponse({'status': 'ya_completada', 'estrellas': progreso.estrellas})

        # Count scoreable activities and correct answers
        tipos_con_correcta = ('listening', 'reading', 'writing', 'pronunciacion', 'minijuego_embed')
        total_scoreable = leccion.actividades.filter(tipo__in=tipos_con_correcta).count()
        correctas       = RespuestaActividad.objects.filter(
            progreso=progreso, es_correcta=True
        ).count()

        estrellas = progreso.calcular_estrellas(total_scoreable, correctas)

        progreso.completada    = True
        progreso.estrellas     = estrellas
        progreso.completada_en = timezone.now()
        progreso.save(update_fields=['completada', 'estrellas', 'completada_en'])

        # Award XP and check level-up
        nivel_subio   = False
        nivel_nuevo   = None
        try:
            perfil = request.user.estudiante_profile
            perfil.puntos_totales += leccion.puntos_xp
            perfil.save(update_fields=['puntos_totales'])
            nivel_subio = perfil.actualizar_nivel()
            nivel_nuevo = perfil.nivel if nivel_subio else None

            # Update total_estrellas_historia
            from apps.accounts.models import EstudianteProfile
            EstudianteProfile.objects.filter(pk=perfil.pk).update(
                total_estrellas_historia=db_models.F('total_estrellas_historia') + estrellas
            )
        except Exception:
            pass

        # Award bones
        huesos = leccion.huesos_recompensa
        try:
            request.user.huesos += huesos
            request.user.save(update_fields=['huesos'])
            HuesoTransaccion.objects.create(
                user=request.user,
                tipo='ganado',
                cantidad=huesos,
                descripcion=f'🎓 Lección completada: {leccion.titulo}',
            )
        except Exception:
            pass

        # Check historia achievements
        from .services import verificar_logros_historia
        logros_nuevos = verificar_logros_historia(request.user, progreso)

        return JsonResponse({
            'status':       'ok',
            'estrellas':    estrellas,
            'puntos_xp':    leccion.puntos_xp,
            'huesos':       huesos,
            'nivel_subio':  nivel_subio,
            'nivel_nuevo':  nivel_nuevo,
            'logros_nuevos': [
                {'nombre': l.nombre, 'icono': l.icono}
                for l in logros_nuevos
            ],
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ── Profesor: panel de secciones ─────────────────────────────────────────────

@login_required
@profesor_required
def panel_historia_profesor(request):
    try:
        prof_profile = request.user.profesor_profile
    except Exception:
        return redirect('accounts:dashboard')

    salones  = prof_profile.salones.filter(is_active=True).order_by('grado', 'nombre')
    secciones = SeccionHistoria.objects.prefetch_related('desbloqueos').order_by('orden')

    # Build a set of (seccion_id, salon_id) that are explicitly unlocked
    desbloqueados = set(
        SeccionDesbloqueada.objects
        .filter(salon__in=salones)
        .values_list('seccion_id', 'salon_id')
    )

    secciones_data = []
    for sec in secciones:
        salones_info = []
        for salon in salones:
            auto        = sec.is_desbloqueada_por_defecto
            desbloqueada = auto or (sec.pk, salon.pk) in desbloqueados
            salones_info.append({
                'salon':       salon,
                'desbloqueada': desbloqueada,
                'auto':        auto,
            })
        secciones_data.append({
            'seccion':      sec,
            'salones_info': salones_info,
        })

    return render(request, 'historia/profesor/panel.html', {
        'secciones_data': secciones_data,
        'salones':        salones,
    })


# ── AJAX: desbloquear / bloquear sección ─────────────────────────────────────

@login_required
@profesor_required
@require_POST
def desbloquear_seccion(request, pk):
    try:
        data     = json.loads(request.body)
        salon_pk = data.get('salon_pk')
        seccion  = get_object_or_404(SeccionHistoria, pk=pk)

        from apps.accounts.models import Salon
        salon = get_object_or_404(
            Salon, pk=salon_pk,
            profesor=request.user.profesor_profile,
        )

        SeccionDesbloqueada.objects.get_or_create(
            seccion=seccion,
            salon=salon,
            defaults={'desbloqueada_por': request.user},
        )
        return JsonResponse({'status': 'ok', 'accion': 'desbloqueada'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@profesor_required
@require_POST
def bloquear_seccion(request, pk):
    try:
        data     = json.loads(request.body)
        salon_pk = data.get('salon_pk')
        seccion  = get_object_or_404(SeccionHistoria, pk=pk)

        from apps.accounts.models import Salon
        salon = get_object_or_404(
            Salon, pk=salon_pk,
            profesor=request.user.profesor_profile,
        )

        SeccionDesbloqueada.objects.filter(
            seccion=seccion, salon=salon
        ).delete()
        return JsonResponse({'status': 'ok', 'accion': 'bloqueada'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ── Profesor: progreso por sección ───────────────────────────────────────────

@login_required
@profesor_required
def progreso_seccion_profesor(request, pk):
    seccion = get_object_or_404(SeccionHistoria, pk=pk)

    try:
        prof_profile = request.user.profesor_profile
    except Exception:
        return redirect('accounts:dashboard')

    salones = prof_profile.salones.filter(is_active=True)
    salon_pk = request.GET.get('salon')

    from apps.accounts.models import EstudianteProfile
    estudiantes_qs = EstudianteProfile.objects.filter(
        salon__in=salones
    ).select_related('user', 'salon')
    if salon_pk:
        estudiantes_qs = estudiantes_qs.filter(salon_id=salon_pk)

    lecciones  = list(seccion.lecciones.order_by('orden'))
    total_lec  = len(lecciones)

    # Collect all ProgresoLeccion for this section in one query
    progresos_map = {}
    for prog in ProgresoLeccion.objects.filter(
        leccion__seccion=seccion,
        estudiante__in=[e.user for e in estudiantes_qs],
        completada=True,
    ).select_related('estudiante', 'leccion'):
        progresos_map.setdefault(prog.estudiante_id, []).append(prog)

    estudiantes_data = []
    for est in estudiantes_qs:
        progs      = progresos_map.get(est.user_id, [])
        completadas = len(progs)
        estrellas   = sum(p.estrellas for p in progs)
        pct         = int(completadas / total_lec * 100) if total_lec else 0
        estudiantes_data.append({
            'estudiante':  est,
            'completadas': completadas,
            'total':       total_lec,
            'estrellas':   estrellas,
            'pct':         pct,
        })

    estudiantes_data.sort(key=lambda x: x['pct'], reverse=True)

    return render(request, 'historia/profesor/progreso_seccion.html', {
        'seccion':          seccion,
        'estudiantes_data': estudiantes_data,
        'salones':          salones,
        'salon_seleccionado': int(salon_pk) if salon_pk else None,
    })
