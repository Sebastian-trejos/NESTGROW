import json
import asyncio

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit

from apps.accounts.decorators import profesor_required
from apps.accounts.models import EstudianteProfile
from .models import MensajeChat
from .services import AsistenteMilo


@profesor_required
def index(request):
    """Vista principal con las dos pestañas: Planear y Analizar."""
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
@profesor_required
def analizar(request):
    """Endpoint AJAX para los análisis de resultados (no WebSocket)."""
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
