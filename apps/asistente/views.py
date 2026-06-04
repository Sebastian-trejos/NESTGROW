import json
import asyncio

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.accounts.decorators import profesor_required
from apps.accounts.models import EstudianteProfile
from .models import MensajeChat
from .services import AsistenteMilo, _get_prompt


@profesor_required
def index(request):
    try:
        perfil_prof = request.user.profesor_profile
        estudiantes = EstudianteProfile.objects.filter(
            profesor=perfil_prof
        ).select_related('user').order_by('user__first_name', 'user__username')
    except Exception:
        estudiantes = EstudianteProfile.objects.none()

    historial = MensajeChat.objects.filter(
        profesor=request.user, modo='planeacion'
    ).order_by('created_at')[:20]

    tab_activa = request.GET.get('tab', 'planear')

    return render(request, 'asistente/index.html', {
        'historial': historial,
        'estudiantes': estudiantes,
        'tab_activa': tab_activa,
    })


@require_POST
@profesor_required
@ratelimit(key='user', rate='30/h', method='POST', block=False)
def chat(request):
    """Endpoint AJAX para el chat de planeación."""
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return JsonResponse(
            {'error': 'Has alcanzado el límite de 30 mensajes por hora. Intenta más tarde.'},
            status=429,
        )

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    mensaje = (body.get('mensaje') or '').strip()
    if not mensaje:
        return JsonResponse({'error': 'El mensaje no puede estar vacío.'}, status=400)

    milo = AsistenteMilo()
    resultado = asyncio.run(milo.chat_planeacion(request.user, mensaje))

    return JsonResponse({
        'texto': resultado['texto'],
        'motor': resultado['motor'],
    })


@require_POST
@profesor_required
@ratelimit(key='user', rate='30/h', method='POST', block=False)
def limpiar_historial(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return JsonResponse(
            {'error': 'Has alcanzado el límite por hora. Intenta de nuevo más tarde.'},
            status=429,
        )
    MensajeChat.objects.filter(profesor=request.user, modo='planeacion').delete()
    return JsonResponse({'ok': True})


@require_POST
@login_required
@ratelimit(key='user', rate='60/h', method='POST', block=False)
def milo_correccion(request):
    """Genera una corrección breve con IA para mostrar al estudiante vía el bubble de Milo."""
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return JsonResponse({'correccion': 'Keep practicing! Consistency leads to success. 💪'})

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'correccion': 'Try again! 💪'})

    pregunta         = (body.get('pregunta') or '').strip()[:300]
    respuesta_correcta = (body.get('respuesta_correcta') or '').strip()[:200]
    respuesta_dada   = (body.get('respuesta_dada') or '').strip()[:200]
    contexto         = (body.get('contexto') or '').strip()[:200]

    partes = []
    if contexto:
        partes.append(f'Context: {contexto}.')
    if pregunta:
        partes.append(f'Question: "{pregunta}".')
    if respuesta_dada:
        partes.append(f'The student answered: "{respuesta_dada}".')
    if respuesta_correcta:
        partes.append(f'The correct answer was: "{respuesta_correcta}".')
    if not partes:
        return JsonResponse({'correccion': "Don't give up! Every mistake teaches you something new. 💪"})

    mensaje = ' '.join(partes) + ' Give the brief correction.'
    messages = [{'role': 'user', 'content': mensaje}]

    milo = AsistenteMilo()
    resultado = asyncio.run(milo._llamar_ia(
        messages, _get_prompt('correccion'),
        proposito='milo_correccion',
        usuario=request.user,
        ttl=3600 * 24 * 7,  # correcciones se cachean 7 días
    ))
    texto = resultado.get('texto', '').strip()
    if not texto or resultado.get('motor') == 'error':
        texto = 'Almost there! The correct answer was: ' + (respuesta_correcta or '…') + '. You can do it! 💪'

    return JsonResponse({'correccion': texto})


@require_POST
@profesor_required
def analizar(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    tipo = body.get('tipo_analisis', '').strip()
    tipos_validos = {'resumen_semanal', 'talleres', 'modo_historia', 'estudiante_detalle'}
    if tipo not in tipos_validos:
        return JsonResponse({'error': 'Tipo de análisis no válido.'}, status=400)

    estudiante_id = body.get('estudiante_id') or None
    if estudiante_id:
        try:
            estudiante_id = int(estudiante_id)
        except (ValueError, TypeError):
            estudiante_id = None

    milo = AsistenteMilo()
    resultado = asyncio.run(
        milo.analizar_resultados(request.user, tipo, estudiante_id)
    )

    return JsonResponse({
        'texto': resultado['texto'],
        'motor': resultado['motor'],
    })
