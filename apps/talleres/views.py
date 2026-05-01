import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import models as db_models

from .models import (
    Taller, BloqueTaller, BloqueMinijuego, BloquePregunta,
    OpcionRespuesta, RespuestaEstudiante, SesionTaller,
)
from .forms import TallerForm
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
@estudiante_required
def mis_talleres(request):
    profile = request.user.estudiante_profile
    if profile.salon:
        talleres = Taller.objects.filter(
            salon=profile.salon, is_active=True
        ).order_by('-created_at')
    else:
        talleres = Taller.objects.none()

    sesiones = {
        s.taller_id: s
        for s in SesionTaller.objects.filter(estudiante=request.user, taller__in=talleres)
    }

    talleres_con_estado = []
    for t in talleres:
        sesion = sesiones.get(t.pk)
        talleres_con_estado.append({
            'taller': t,
            'sesion': sesion,
            'completado': sesion.completada if sesion else False,
            'en_progreso': bool(sesion and not sesion.completada and sesion.bloque_actual > 0),
        })

    return render(request, 'talleres/estudiante/mis_talleres.html', {
        'talleres_con_estado': talleres_con_estado,
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
        return redirect('talleres:resultado', pk=taller.pk)

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
        return JsonResponse({'ok': True, 'next': 'resultado', 'es_correcta': es_correcta, 'puntos': puntos})

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
        return JsonResponse({'ok': True, 'next': 'resultado'})

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
        sesion.huesos_ganados = taller.huesos_recompensa
        sesion.save()

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

        # Desbloquear vocabulario y verificar hitos
        palabras_nuevas = desbloquear_vocabulario_taller(sesion)
        hitos_nuevos = verificar_hitos_vocabulario(request.user)

    return render(request, 'talleres/estudiante/resultado.html', {
        'taller': taller,
        'sesion': sesion,
        'subio_nivel': subio_nivel,
        'palabras_nuevas': palabras_nuevas,
        'hitos_nuevos': hitos_nuevos,
    })
