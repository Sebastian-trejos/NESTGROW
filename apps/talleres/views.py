import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import models as db_models
from django.utils import timezone

from .models import (
    Taller, BloqueTaller, BloqueMinijuego, BloquePregunta,
    OpcionRespuesta, RespuestaEstudiante, SesionTaller,
    Periodo, AsignacionTaller, AsignacionMinijuego, RegistroMinijuegoPeriodo,
)
from .forms import TallerForm, PeriodoForm
from apps.accounts.decorators import profesor_required, estudiante_required
from apps.accounts.models import Salon
from apps.games.models import Game, HuesoTransaccion
from apps.content.utils import desbloquear_vocabulario_taller, verificar_hitos_vocabulario


# ── Helpers ───────────────────────────────────────────────────────────────────

def _salon_qs(user):
    try:
        return Salon.objects.filter(profesor=user.profesor_profile)
    except Exception:
        return Salon.objects.none()


# ── Profesor — CRUD Taller ────────────────────────────────────────────────────

@login_required
@profesor_required
def lista_talleres(request):
    talleres = (
        Taller.objects.filter(profesor=request.user)
        .prefetch_related('bloques', 'sesiones')
        .order_by('-created_at')
    )
    return render(request, 'talleres/profesor/lista.html', {'talleres': talleres})


@login_required
@profesor_required
def crear_taller(request):
    if request.method == 'POST':
        form = TallerForm(request.POST)
        form.fields['salon'].queryset = _salon_qs(request.user)
        if form.is_valid():
            taller = form.save(commit=False)
            taller.profesor = request.user
            taller.save()
            messages.success(request, f'✅ Taller "{taller.titulo}" creado. ¡Ahora añade los bloques!')
            return redirect('talleres:editar', pk=taller.pk)
    else:
        form = TallerForm()
        form.fields['salon'].queryset = _salon_qs(request.user)
    return render(request, 'talleres/profesor/form.html', {
        'form': form, 'taller': None, 'titulo': 'Nuevo Taller',
    })


@login_required
@profesor_required
def editar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    if request.method == 'POST':
        form = TallerForm(request.POST, instance=taller)
        form.fields['salon'].queryset = _salon_qs(request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Taller actualizado.')
            return redirect('talleres:editar', pk=taller.pk)
    else:
        form = TallerForm(instance=taller)
        form.fields['salon'].queryset = _salon_qs(request.user)

    bloques = list(
        taller.bloques.order_by('orden')
        .select_related('bloque_minijuego__game', 'bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
    )
    juegos_disponibles = Game.objects.select_related('category').order_by('category__name', 'title')

    return render(request, 'talleres/profesor/form.html', {
        'form': form,
        'taller': taller,
        'bloques': bloques,
        'juegos_disponibles': juegos_disponibles,
        'titulo': f'Editar: {taller.titulo}',
    })


@login_required
@profesor_required
def eliminar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    if request.method == 'POST':
        titulo = taller.titulo
        taller.delete()
        messages.success(request, f'🗑️ Taller "{titulo}" eliminado.')
        return redirect('talleres:lista')
    return render(request, 'talleres/profesor/confirmar_eliminar.html', {'taller': taller})


@login_required
@profesor_required
@require_POST
def toggle_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    taller.is_active = not taller.is_active
    taller.save(update_fields=['is_active'])
    estado = '✅ publicado' if taller.is_active else '🔒 ocultado'
    messages.success(request, f'Taller {estado}.')
    return redirect('talleres:lista')


@login_required
@profesor_required
def preview_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    bloques = (
        taller.bloques.order_by('orden')
        .select_related('bloque_minijuego__game', 'bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
    )
    return render(request, 'talleres/profesor/preview.html', {
        'taller': taller, 'bloques': bloques,
    })


# ── Profesor — AJAX Bloques ───────────────────────────────────────────────────

@login_required
@profesor_required
@require_POST
def agregar_bloque(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    tipo = request.POST.get('tipo')
    if tipo not in ('pregunta', 'minijuego'):
        return JsonResponse({'error': 'Tipo inválido'}, status=400)

    ultimo = taller.bloques.aggregate(m=db_models.Max('orden'))['m'] or 0
    bloque = BloqueTaller.objects.create(taller=taller, orden=ultimo + 1, tipo=tipo)

    if tipo == 'minijuego':
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, pk=game_id)
        BloqueMinijuego.objects.create(bloque=bloque, game=game)
        descripcion = f"{game.get_game_type_display()} — {game.title}"

    else:  # pregunta
        enunciado = request.POST.get('enunciado', '').strip()
        tipo_respuesta = request.POST.get('tipo_respuesta', 'opcion_multiple')
        puntaje_parcial = max(1, int(request.POST.get('puntaje_parcial', 10) or 10))
        video_url = request.POST.get('video_url', '')

        pregunta = BloquePregunta(
            bloque=bloque,
            enunciado=enunciado,
            tipo_respuesta=tipo_respuesta,
            puntaje_parcial=puntaje_parcial,
            video_url=video_url,
        )
        if request.FILES.get('imagen'):
            pregunta.imagen = request.FILES['imagen']
        if request.FILES.get('video_archivo'):
            pregunta.video_archivo = request.FILES['video_archivo']
        pregunta.save()

        if tipo_respuesta in ('opcion_multiple', 'casillas'):
            try:
                opciones = json.loads(request.POST.get('opciones', '[]'))
            except Exception:
                opciones = []
            for op in opciones:
                texto = (op.get('texto') or '').strip()
                if texto:
                    OpcionRespuesta.objects.create(
                        pregunta=pregunta,
                        texto=texto,
                        es_correcta=bool(op.get('es_correcta', False)),
                    )

        descripcion = enunciado[:60]

    return JsonResponse({
        'ok': True,
        'bloque_id': bloque.pk,
        'orden': bloque.orden,
        'tipo': tipo,
        'descripcion': descripcion,
    })


@login_required
@profesor_required
@require_POST
def eliminar_bloque(request, bpk):
    bloque = get_object_or_404(BloqueTaller, pk=bpk, taller__profesor=request.user)
    bloque.delete()
    return JsonResponse({'ok': True})


@login_required
@profesor_required
@require_POST
def mover_bloques(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)
    try:
        data = json.loads(request.body)
        orden_ids = data.get('orden', [])
    except Exception:
        return JsonResponse({'error': 'Formato inválido'}, status=400)
    for i, bloque_id in enumerate(orden_ids):
        BloqueTaller.objects.filter(pk=bloque_id, taller=taller).update(orden=i + 1)
    return JsonResponse({'ok': True})


# ── Estudiante ────────────────────────────────────────────────────────────────

@login_required
@profesor_required
def resultados_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, profesor=request.user)

    sesiones = (
        SesionTaller.objects
        .filter(taller=taller)
        .select_related('estudiante', 'estudiante__estudiante_profile')
        .prefetch_related(
            'estudiante__respuestas_taller__pregunta__opciones',
            'estudiante__respuestas_taller__opciones_elegidas',
        )
        .order_by('-completada', '-puntos_obtenidos', 'estudiante__first_name')
    )

    bloques_pregunta = list(
        taller.bloques
        .filter(tipo='pregunta')
        .select_related('bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
        .order_by('orden')
    )

    total = sesiones.count()
    completadas = sesiones.filter(completada=True).count()
    promedio = 0
    if completadas:
        from django.db.models import Avg
        promedio = round(
            sesiones.filter(completada=True).aggregate(p=Avg('puntos_obtenidos'))['p'] or 0, 1
        )

    # Armar datos por sesión: lista de respuestas ordenadas por bloque
    sesiones_data = []
    for sesion in sesiones:
        respuestas_map = {
            r.pregunta_id: r
            for r in sesion.estudiante.respuestas_taller.filter(
                pregunta__bloque__taller=taller
            ).prefetch_related('opciones_elegidas')
        }
        bloques_con_respuesta = []
        for b in bloques_pregunta:
            pregunta = getattr(b, 'bloque_pregunta', None)
            if pregunta:
                bloques_con_respuesta.append({
                    'bloque': b,
                    'pregunta': pregunta,
                    'respuesta': respuestas_map.get(pregunta.pk),
                })
        sesiones_data.append({
            'sesion': sesion,
            'bloques': bloques_con_respuesta,
        })

    return render(request, 'talleres/profesor/resultados.html', {
        'taller': taller,
        'sesiones_data': sesiones_data,
        'total': total,
        'completadas': completadas,
        'en_progreso': total - completadas,
        'promedio': promedio,
        'total_puntos_posibles': taller.total_puntos_posibles(),
    })


@login_required
@estudiante_required
def mis_talleres(request):
    """Panel principal del estudiante: muestra actividades del período activo."""
    from django.utils import timezone as tz

    profile = request.user.estudiante_profile
    periodo_activo = None
    talleres_pendientes = []
    minijuegos_pendientes = []

    # Marcar minijuego como revisado si viene del overlay de victoria
    registro_pk = request.GET.get('revisado')
    if registro_pk:
        RegistroMinijuegoPeriodo.objects.filter(
            pk=registro_pk, estudiante=request.user
        ).update(revisado=True)

    if profile.salon:
        hoy = tz.now().date()
        periodo_activo = Periodo.objects.filter(
            salon=profile.salon,
            is_activo=True,
            cerrado=False,
            fecha_fin__gte=hoy,
        ).order_by('-fecha_inicio').first()

        if periodo_activo:
            # Talleres asignados que no estén completados+revisados
            sesiones_map = {
                s.taller_id: s
                for s in SesionTaller.objects.filter(
                    estudiante=request.user,
                    taller__in=periodo_activo.talleres_asignados.values_list('taller_id', flat=True),
                )
            }
            for asig in periodo_activo.talleres_asignados.select_related('taller').order_by('orden'):
                sesion = sesiones_map.get(asig.taller_id)
                completado = sesion.completada if sesion else False
                revisado = sesion.revisado if sesion else False
                if not (completado and revisado):
                    talleres_pendientes.append({
                        'asignacion': asig,
                        'taller': asig.taller,
                        'sesion': sesion,
                        'completado': completado,
                        'en_progreso': bool(sesion and not sesion.completada and sesion.bloque_actual > 0),
                    })

            # Minijuegos asignados que no estén revisados
            registros_map = {
                r.asignacion_id: r
                for r in RegistroMinijuegoPeriodo.objects.filter(
                    periodo=periodo_activo, estudiante=request.user
                )
            }
            for asig in periodo_activo.minijuegos_asignados.select_related('game').order_by('orden'):
                registro = registros_map.get(asig.pk)
                revisado = registro.revisado if registro else False
                if not revisado:
                    minijuegos_pendientes.append({
                        'asignacion': asig,
                        'game': asig.game,
                        'registro': registro,
                        'completado': registro.completado if registro else False,
                    })

    return render(request, 'talleres/estudiante/mis_talleres.html', {
        'periodo_activo': periodo_activo,
        'talleres_pendientes': talleres_pendientes,
        'minijuegos_pendientes': minijuegos_pendientes,
    })


@login_required
@estudiante_required
def resolver_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk, is_active=True)
    profile = request.user.estudiante_profile

    if taller.salon and taller.salon != profile.salon:
        messages.error(request, '⛔ Este taller no está asignado a tu salón.')
        return redirect('talleres:mis_talleres')

    sesion, _ = SesionTaller.objects.get_or_create(
        taller=taller, estudiante=request.user,
        defaults={'bloque_actual': 0},
    )

    if sesion.completada:
        # Si la sesión no fue revisada aún, ir a la pantalla de resultado_sesion (flujo Periodo)
        if not sesion.revisado:
            return redirect('talleres:resultado_sesion', pk=sesion.pk)
        return redirect('talleres:mis_talleres')

    bloques = list(
        taller.bloques.order_by('orden')
        .select_related('bloque_minijuego__game', 'bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
    )

    if not bloques:
        messages.warning(request, '⚠️ Este taller no tiene bloques todavía.')
        return redirect('talleres:mis_talleres')

    idx = sesion.bloque_actual
    if idx >= len(bloques):
        return redirect('talleres:resultado', pk=taller.pk)

    return render(request, 'talleres/estudiante/resolver.html', {
        'taller': taller,
        'sesion': sesion,
        'bloque_actual': bloques[idx],
        'bloque_idx': idx,
        'total_bloques': len(bloques),
    })


@login_required
@estudiante_required
@require_POST
def guardar_respuesta(request, pk, bpk):
    taller = get_object_or_404(Taller, pk=pk, is_active=True)
    bloque = get_object_or_404(BloqueTaller, pk=bpk, taller=taller, tipo='pregunta')
    pregunta = get_object_or_404(BloquePregunta, bloque=bloque)
    sesion = get_object_or_404(SesionTaller, taller=taller, estudiante=request.user)

    if sesion.completada:
        return JsonResponse({'error': 'Taller ya completado'}, status=400)

    bloques_ids = list(taller.bloques.order_by('orden').values_list('pk', flat=True))
    if sesion.bloque_actual >= len(bloques_ids) or bloques_ids[sesion.bloque_actual] != bpk:
        return JsonResponse({'error': 'No es el bloque actual'}, status=400)

    # Eliminar respuesta anterior si existe
    RespuestaEstudiante.objects.filter(estudiante=request.user, pregunta=pregunta).delete()

    respuesta = RespuestaEstudiante(estudiante=request.user, pregunta=pregunta)
    es_correcta = None

    if pregunta.tipo_respuesta == 'parrafo':
        respuesta.texto_respuesta = request.POST.get('texto_respuesta', '').strip()
        respuesta.es_correcta = None
        respuesta.save()
    else:
        respuesta.save()
        opciones_ids = [int(x) for x in request.POST.getlist('opciones') if x.isdigit()]
        respuesta.opciones_elegidas.set(opciones_ids)
        correctas = set(pregunta.opciones.filter(es_correcta=True).values_list('pk', flat=True))
        elegidas = set(opciones_ids)
        respuesta.es_correcta = (elegidas == correctas)
        es_correcta = respuesta.es_correcta
        respuesta.save()

    puntos = pregunta.puntaje_parcial if es_correcta else 0
    sesion.puntos_obtenidos += puntos
    sesion.bloque_actual += 1
    sesion.save()

    if sesion.bloque_actual >= len(bloques_ids):
        return JsonResponse({'ok': True, 'next': 'resultado', 'sesion_pk': sesion.pk, 'es_correcta': es_correcta, 'puntos': puntos})

    return JsonResponse({'ok': True, 'next': 'siguiente', 'es_correcta': es_correcta, 'puntos': puntos})


@login_required
@estudiante_required
@require_POST
def score_bloque_minijuego(request, pk, bpk):
    taller = get_object_or_404(Taller, pk=pk, is_active=True)
    bloque = get_object_or_404(BloqueTaller, pk=bpk, taller=taller, tipo='minijuego')
    sesion = get_object_or_404(SesionTaller, taller=taller, estudiante=request.user)

    if sesion.completada:
        return JsonResponse({'error': 'Taller ya completado'}, status=400)

    bloques_ids = list(taller.bloques.order_by('orden').values_list('pk', flat=True))
    if sesion.bloque_actual >= len(bloques_ids) or bloques_ids[sesion.bloque_actual] != bpk:
        return JsonResponse({'error': 'No es el bloque actual'}, status=400)

    sesion.puntos_obtenidos += bloque.bloque_minijuego.game.points_reward
    sesion.bloque_actual += 1
    sesion.save()

    if sesion.bloque_actual >= len(bloques_ids):
        return JsonResponse({'ok': True, 'next': 'resultado', 'sesion_pk': sesion.pk})

    return JsonResponse({'ok': True, 'next': 'siguiente'})


@login_required
@estudiante_required
def resultado_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    try:
        sesion = SesionTaller.objects.get(taller=taller, estudiante=request.user)
    except SesionTaller.DoesNotExist:
        return redirect('talleres:mis_talleres')

    subio_nivel = False
    palabras_nuevas = []
    hitos_nuevos = []

    if not sesion.completada:
        sesion.completada = True
        sesion.completada_en = timezone.now()
        sesion.huesos_ganados = taller.huesos_recompensa
        # Guardar con update_fields para que el signal de huesos se dispare correctamente
        sesion.save(update_fields=['completada', 'completada_en', 'huesos_ganados', 'bloque_actual'])

        profile = request.user.estudiante_profile
        profile.puntos_totales += taller.puntos_xp
        subio_nivel = profile.actualizar_nivel()

        if taller.huesos_recompensa > 0:
            request.user.huesos += taller.huesos_recompensa
            request.user.save(update_fields=['huesos'])
            HuesoTransaccion.objects.create(
                user=request.user,
                tipo='ganado',
                cantidad=taller.huesos_recompensa,
                descripcion=f'🎓 Completaste el taller: {taller.titulo}',
            )

        # Notificación WebSocket de nivel subido (se hace aquí porque la señal
        # de SesionTaller se dispara antes de actualizar_nivel())
        if subio_nivel:
            try:
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'usuario_{request.user.pk}',
                        {'type': 'nivel_subido', 'nivel': profile.nivel},
                    )
            except Exception:
                pass

        # Desbloquear vocabulario y verificar hitos
        palabras_nuevas = desbloquear_vocabulario_taller(sesion)
        hitos_nuevos = verificar_hitos_vocabulario(request.user)

    # Resumen de respuestas ordenado por posición del bloque
    bloques_pregunta = list(
        taller.bloques
        .filter(tipo='pregunta')
        .select_related('bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
        .order_by('orden')
    )
    respuestas_map = {
        r.pregunta_id: r
        for r in RespuestaEstudiante.objects
        .filter(estudiante=request.user, pregunta__bloque__taller=taller)
        .prefetch_related('opciones_elegidas')
    }
    resumen_respuestas = []
    for b in bloques_pregunta:
        pregunta = getattr(b, 'bloque_pregunta', None)
        if pregunta:
            resumen_respuestas.append({
                'bloque': b,
                'pregunta': pregunta,
                'respuesta': respuestas_map.get(pregunta.pk),
            })

    return render(request, 'talleres/estudiante/resultado.html', {
        'taller': taller,
        'sesion': sesion,
        'subio_nivel': subio_nivel,
        'palabras_nuevas': palabras_nuevas,
        'hitos_nuevos': hitos_nuevos,
        'resumen_respuestas': resumen_respuestas,
    })


# ── Periodos — Profesor ────────────────────────────────────────────────────────

@login_required
@profesor_required
def lista_periodos(request):
    """Lista todos los períodos del profesor, agrupados por salón."""
    from django.utils import timezone as tz
    salones = _salon_qs(request.user).prefetch_related('periodos')
    periodos = Periodo.objects.filter(
        salon__in=salones
    ).select_related('salon').prefetch_related(
        'talleres_asignados__taller', 'minijuegos_asignados__game'
    ).order_by('-fecha_inicio')

    return render(request, 'talleres/profesor/lista_periodos.html', {
        'periodos': periodos,
        'hoy': tz.now().date(),
    })


@login_required
@profesor_required
def crear_periodo(request):
    """El profesor crea un nuevo período con sus asignaciones."""
    salon_qs = _salon_qs(request.user)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, salon_qs=salon_qs)
        # Filtrar talleres del salón seleccionado dinámicamente
        salon_id = request.POST.get('salon')
        if salon_id:
            form.fields['talleres_asignados'].queryset = Taller.objects.filter(
                salon_id=salon_id, is_active=True
            )
        if form.is_valid():
            periodo = form.save()
            # Crear asignaciones
            for i, taller in enumerate(form.cleaned_data['talleres_asignados'], start=1):
                AsignacionTaller.objects.create(periodo=periodo, taller=taller, orden=i)
            for i, game in enumerate(form.cleaned_data['minijuegos_asignados'], start=1):
                AsignacionMinijuego.objects.create(periodo=periodo, game=game, orden=i)
            messages.success(request, f'✅ Período "{periodo.titulo}" creado exitosamente.')
            return redirect('talleres:lista_periodos')
    else:
        form = PeriodoForm(salon_qs=salon_qs)
    # Para el JS que filtra talleres por salón
    talleres_por_salon = {}
    for salon in salon_qs:
        talleres_por_salon[salon.pk] = list(
            Taller.objects.filter(salon=salon, is_active=True).values('pk', 'titulo')
        )
    import json as _json
    return render(request, 'talleres/profesor/crear_periodo.html', {
        'form': form,
        'talleres_por_salon_json': _json.dumps(talleres_por_salon),
    })


@login_required
@profesor_required
def resultados_periodo(request, pk):
    """Vista consolidada: por cada estudiante del salón, muestra su avance en el período."""
    salon_qs = _salon_qs(request.user)
    periodo = get_object_or_404(Periodo, pk=pk, salon__in=salon_qs)

    from django.utils import timezone as tz
    from apps.accounts.models import CustomUser

    # Estudiantes del salón
    estudiantes = CustomUser.objects.filter(
        estudiante_profile__salon=periodo.salon, role='estudiante'
    ).select_related('estudiante_profile').order_by('first_name', 'last_name', 'username')

    talleres_asig = list(periodo.talleres_asignados.select_related('taller').order_by('orden'))
    minijuegos_asig = list(periodo.minijuegos_asignados.select_related('game').order_by('orden'))

    # Precargar sesiones y registros
    sesiones_all = {
        (s.taller_id, s.estudiante_id): s
        for s in SesionTaller.objects.filter(
            taller__in=[a.taller for a in talleres_asig],
            estudiante__in=estudiantes,
        )
    }
    registros_all = {
        (r.asignacion_id, r.estudiante_id): r
        for r in RegistroMinijuegoPeriodo.objects.filter(
            periodo=periodo, estudiante__in=estudiantes,
        )
    }

    filas = []
    for est in estudiantes:
        fila_talleres = []
        for asig in talleres_asig:
            sesion = sesiones_all.get((asig.taller_id, est.pk))
            pts = sesion.puntos_obtenidos if sesion else 0
            max_pts = asig.taller.total_puntos_posibles() or 1
            pct = round((pts / max_pts) * 100) if sesion and sesion.completada else None
            from apps.games.models import pct_to_nota
            nota = pct_to_nota(pct) if pct is not None else None
            fila_talleres.append({
                'asig': asig,
                'sesion': sesion,
                'pct': pct,
                'nota': nota,
            })

        fila_minijuegos = []
        for asig in minijuegos_asig:
            registro = registros_all.get((asig.pk, est.pk))
            fila_minijuegos.append({
                'asig': asig,
                'registro': registro,
            })

        estrellas = getattr(getattr(est, 'estudiante_profile', None), 'total_estrellas_historia', 0) or 0
        filas.append({
            'estudiante': est,
            'talleres': fila_talleres,
            'minijuegos': fila_minijuegos,
            'estrellas_historia': estrellas,
        })

    return render(request, 'talleres/profesor/resultados_periodo.html', {
        'periodo': periodo,
        'talleres_asig': talleres_asig,
        'minijuegos_asig': minijuegos_asig,
        'filas': filas,
        'hoy': tz.now().date(),
    })


@login_required
@profesor_required
@require_POST
def cerrar_periodo(request, pk):
    """Cierra un período — congela resultados."""
    salon_qs = _salon_qs(request.user)
    periodo = get_object_or_404(Periodo, pk=pk, salon__in=salon_qs)
    if not periodo.cerrado:
        periodo.cerrado = True
        periodo.is_activo = False
        periodo.save(update_fields=['cerrado', 'is_activo'])
        messages.success(request, f'🔒 Período "{periodo.titulo}" cerrado. Los resultados quedaron congelados.')
    return redirect('talleres:resultados_periodo', pk=pk)


# ── Periodos — Estudiante ─────────────────────────────────────────────────────

@login_required
@estudiante_required
def resultado_sesion(request, pk):
    """Pantalla de resultado post-taller. Al volver al panel marca la sesión como revisada."""
    sesion = get_object_or_404(SesionTaller, pk=pk, estudiante=request.user)
    taller = sesion.taller

    if request.method == 'POST':
        # El estudiante hizo clic en "Volver al panel"
        sesion.revisado = True
        sesion.save(update_fields=['revisado'])
        return redirect('talleres:mis_talleres')

    # Calcular nota
    max_pts = taller.total_puntos_posibles() or 1
    pct = round((sesion.puntos_obtenidos / max_pts) * 100) if sesion.completada else 0
    from apps.games.models import pct_to_nota
    nota = pct_to_nota(pct) if sesion.completada else None

    # Resumen de respuestas
    bloques_pregunta = list(
        taller.bloques.filter(tipo='pregunta')
        .select_related('bloque_pregunta')
        .prefetch_related('bloque_pregunta__opciones')
        .order_by('orden')
    )
    respuestas_map = {
        r.pregunta_id: r
        for r in RespuestaEstudiante.objects.filter(
            estudiante=request.user, pregunta__bloque__taller=taller
        ).prefetch_related('opciones_elegidas')
    }
    resumen = []
    for b in bloques_pregunta:
        pregunta = getattr(b, 'bloque_pregunta', None)
        if pregunta:
            resumen.append({
                'bloque': b,
                'pregunta': pregunta,
                'respuesta': respuestas_map.get(pregunta.pk),
            })

    return render(request, 'talleres/estudiante/resultado_sesion.html', {
        'sesion': sesion,
        'taller': taller,
        'pct': pct,
        'nota': nota,
        'resumen': resumen,
    })
