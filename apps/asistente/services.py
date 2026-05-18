import json
import logging
from datetime import timedelta

import httpx
from django.conf import settings
from django.utils import timezone

from .models import MensajeChat

logger = logging.getLogger(__name__)

GEMINI_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    'gemini-2.0-flash:generateContent'
)
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

SYSTEM_PLANEACION = (
    'Eres el Asistente Milo, un ayudante educativo especializado para profesores de inglés '
    'en primaria colombiana. Tu rol es ayudar a planear talleres de inglés, generar preguntas '
    'creativas listas para copiar, sugerir actividades lúdicas, proporcionar vocabulario con '
    'ejemplos, y adaptar contenido al nivel de los niños de primaria. Siempre responde en '
    'español. Sé conciso y práctico. Cuando generes preguntas o actividades, dálas en formato '
    'claro y numerado, listo para usar directamente en el programa.'
)


class AsistenteMilo:

    # ── IA core ───────────────────────────────────────────────────────────────

    async def _llamar_ia(self, messages: list[dict], system_prompt: str) -> dict:
        """Intenta Gemini, fallback Groq. Retorna {'texto': ..., 'motor': ...}."""
        try:
            resultado = await self._gemini(messages, system_prompt)
            if resultado:
                return {'texto': resultado, 'motor': 'gemini'}
        except Exception as exc:
            logger.warning('Gemini falló: %s', exc)

        try:
            resultado = await self._groq(messages, system_prompt)
            if resultado:
                return {'texto': resultado, 'motor': 'groq'}
        except Exception as exc:
            logger.warning('Groq falló: %s', exc)

        return {
            'texto': 'El asistente no está disponible en este momento. Intenta más tarde.',
            'motor': 'error',
        }

    async def _gemini(self, messages: list[dict], system_prompt: str) -> str | None:
        contents = []
        for m in messages:
            role = 'user' if m['role'] == 'user' else 'model'
            contents.append({'role': role, 'parts': [{'text': m['content']}]})

        payload = {
            'system_instruction': {'parts': [{'text': system_prompt}]},
            'contents': contents,
            'generationConfig': {'maxOutputTokens': 1024, 'temperature': 0.7},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GEMINI_URL,
                headers={'x-goog-api-key': settings.GEMINI_API_KEY},
                json=payload,
            )
        if resp.status_code != 200:
            logger.warning('Gemini HTTP %s: %s', resp.status_code, resp.text[:300])
            return None
        data = resp.json()
        return data['candidates'][0]['content']['parts'][0]['text']

    async def _groq(self, messages: list[dict], system_prompt: str) -> str | None:
        groq_messages = [{'role': 'system', 'content': system_prompt}] + messages
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': groq_messages,
            'max_tokens': 1024,
            'temperature': 0.7,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={'Authorization': f'Bearer {settings.GROQ_API_KEY}'},
                json=payload,
            )
        if resp.status_code != 200:
            logger.warning('Groq HTTP %s: %s', resp.status_code, resp.text[:300])
            return None
        data = resp.json()
        return data['choices'][0]['message']['content']

    # ── Chat de planeación ────────────────────────────────────────────────────

    async def chat_planeacion(self, profesor, mensaje_usuario: str) -> dict:
        from asgiref.sync import sync_to_async

        historial = await sync_to_async(list)(
            MensajeChat.objects.filter(profesor=profesor, modo='planeacion')
            .order_by('-created_at')[:20]
        )
        historial.reverse()

        messages = [
            {'role': msg.rol, 'content': msg.contenido}
            for msg in historial
        ]
        messages.append({'role': 'user', 'content': mensaje_usuario})

        resultado = await self._llamar_ia(messages, SYSTEM_PLANEACION)

        await sync_to_async(MensajeChat.objects.create)(
            profesor=profesor,
            rol='user',
            contenido=mensaje_usuario,
            modo='planeacion',
        )
        await sync_to_async(MensajeChat.objects.create)(
            profesor=profesor,
            rol='assistant',
            contenido=resultado['texto'],
            modo='planeacion',
            motor_usado=resultado['motor'],
        )
        await sync_to_async(MensajeChat.limpiar_historial_anterior)(
            profesor, 'planeacion'
        )

        return resultado

    # ── Análisis de resultados ────────────────────────────────────────────────

    async def analizar_resultados(
        self, profesor, tipo_analisis: str, estudiante_id: int | None = None
    ) -> dict:
        from asgiref.sync import sync_to_async

        datos = await sync_to_async(self._recolectar_datos)(
            profesor, tipo_analisis, estudiante_id
        )

        if datos.get('sin_datos'):
            return {
                'texto': (
                    'Aún no hay suficientes datos para generar este análisis. '
                    'Asigna talleres y espera a que tus estudiantes avancen.'
                ),
                'motor': 'sin_datos',
            }

        system_prompt = (
            'Eres un asistente educativo. Analiza estos datos reales de mi salón de clases '
            'y dame un resumen claro en español, con observaciones concretas y 2 o 3 '
            'recomendaciones prácticas que pueda aplicar esta semana. '
            f'Datos: {json.dumps(datos, ensure_ascii=False, default=str)}'
        )
        messages = [{'role': 'user', 'content': '¿Cuál es tu análisis de estos datos?'}]
        return await self._llamar_ia(messages, system_prompt)

    # ── Recolección de datos ──────────────────────────────────────────────────

    def _recolectar_datos(
        self, profesor, tipo_analisis: str, estudiante_id: int | None
    ) -> dict:
        if tipo_analisis == 'resumen_semanal':
            return self._datos_resumen_semanal(profesor)
        if tipo_analisis == 'talleres':
            return self._datos_talleres(profesor)
        if tipo_analisis == 'modo_historia':
            return self._datos_modo_historia(profesor)
        if tipo_analisis == 'estudiante_detalle':
            return self._datos_estudiante(profesor, estudiante_id)
        return {'sin_datos': True}

    def _get_perfil_y_estudiantes(self, profesor):
        """Retorna (profesor_profile, lista_de_user_ids) o (None, []) si no hay salón."""
        from apps.accounts.models import EstudianteProfile
        try:
            perfil_prof = profesor.profesor_profile
        except Exception:
            return None, []
        ids = list(
            EstudianteProfile.objects.filter(profesor=perfil_prof)
            .values_list('user_id', flat=True)
        )
        return perfil_prof, ids

    def _datos_resumen_semanal(self, profesor) -> dict:
        from apps.talleres.models import SesionTaller
        from apps.historia.models import ProgresoLeccion
        from django.contrib.auth import get_user_model
        from django.db.models import Count

        User = get_user_model()
        perfil_prof, estudiantes_ids = self._get_perfil_y_estudiantes(profesor)
        if not estudiantes_ids:
            return {'sin_datos': True}

        hace_7_dias = timezone.now() - timedelta(days=7)

        sesiones = SesionTaller.objects.filter(
            estudiante_id__in=estudiantes_ids,
            completada=True,
            updated_at__gte=hace_7_dias,
        )
        total_sesiones = sesiones.count()
        puntos_obtenidos = sum(s.puntos_obtenidos or 0 for s in sesiones)

        lecciones_semana = ProgresoLeccion.objects.filter(
            estudiante_id__in=estudiantes_ids,
            completada=True,
            updated_at__gte=hace_7_dias,
        ).count()

        top3 = list(
            SesionTaller.objects.filter(
                estudiante_id__in=estudiantes_ids,
                updated_at__gte=hace_7_dias,
            )
            .values('estudiante__username')
            .annotate(total=Count('id'))
            .order_by('-total')[:3]
        )
        activos_ids = set(
            SesionTaller.objects.filter(
                estudiante_id__in=estudiantes_ids,
                updated_at__gte=hace_7_dias,
            ).values_list('estudiante_id', flat=True)
        )
        inactivos = list(
            User.objects.filter(id__in=estudiantes_ids)
            .exclude(id__in=activos_ids)
            .values_list('username', flat=True)
        )

        return {
            'tipo': 'resumen_semanal',
            'total_sesiones_completadas': total_sesiones,
            'puntos_obtenidos': puntos_obtenidos,
            'lecciones_historia_completadas': lecciones_semana,
            'top3_estudiantes': top3,
            'estudiantes_inactivos': inactivos,
        }

    def _datos_talleres(self, profesor) -> dict:
        from apps.talleres.models import Taller, SesionTaller, RespuestaEstudiante
        from django.db.models import Avg, Count

        talleres = Taller.objects.filter(profesor=profesor, is_active=True)
        if not talleres.exists():
            return {'sin_datos': True}

        resultado = []
        for taller in talleres:
            sesiones = SesionTaller.objects.filter(taller=taller)
            completadas = sesiones.filter(completada=True)
            avg_puntos = completadas.aggregate(avg=Avg('puntos_obtenidos'))['avg'] or 0

            bloque_mas_errores = None
            try:
                error_q = (
                    RespuestaEstudiante.objects.filter(
                        pregunta__bloque__taller=taller,
                        es_correcta=False,
                    )
                    .values('pregunta__id', 'pregunta__enunciado')
                    .annotate(total_errores=Count('id'))
                    .order_by('-total_errores')
                    .first()
                )
                if error_q:
                    bloque_mas_errores = {
                        'enunciado': error_q['pregunta__enunciado'][:80],
                        'errores': error_q['total_errores'],
                    }
            except Exception:
                pass

            resultado.append({
                'taller': taller.titulo,
                'estudiantes_completaron': completadas.count(),
                'total_sesiones': sesiones.count(),
                'promedio_puntos': round(avg_puntos, 1),
                'puntos_posibles': taller.total_puntos_posibles(),
                'bloque_mas_errores': bloque_mas_errores,
            })

        return {'tipo': 'talleres', 'talleres': resultado}

    def _datos_modo_historia(self, profesor) -> dict:
        from apps.historia.models import (
            SeccionHistoria, ProgresoLeccion, RespuestaActividad
        )
        from django.db.models import Avg, Count

        perfil_prof, estudiantes_ids = self._get_perfil_y_estudiantes(profesor)
        if not estudiantes_ids:
            return {'sin_datos': True}

        total_estudiantes = len(estudiantes_ids)

        secciones = SeccionHistoria.objects.all().prefetch_related('lecciones')
        datos_secciones = []
        for seccion in secciones:
            lecciones = seccion.lecciones.all()
            total_lecciones = lecciones.count()
            if total_lecciones == 0:
                continue
            completadas = ProgresoLeccion.objects.filter(
                leccion__in=lecciones,
                estudiante_id__in=estudiantes_ids,
                completada=True,
            ).count()
            pct = round(
                (completadas / (total_estudiantes * total_lecciones)) * 100, 1
            )
            datos_secciones.append({'seccion': seccion.titulo, 'pct_completado': pct})

        leccion_problematica = None
        try:
            errores = (
                RespuestaActividad.objects.filter(
                    progreso__estudiante_id__in=estudiantes_ids,
                    es_correcta=False,
                )
                .values('actividad__leccion__titulo')
                .annotate(total=Count('id'))
                .order_by('-total')
                .first()
            )
            if errores:
                leccion_problematica = errores['actividad__leccion__titulo']
        except Exception:
            pass

        progreso_por_est = []
        for uid in estudiantes_ids:
            completadas_est = ProgresoLeccion.objects.filter(
                estudiante_id=uid, completada=True
            ).count()
            progreso_por_est.append(completadas_est)

        if progreso_por_est:
            promedio = sum(progreso_por_est) / len(progreso_por_est)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            rezagados = list(
                User.objects.filter(id__in=[
                    uid for uid, prog in zip(estudiantes_ids, progreso_por_est)
                    if prog < promedio * 0.5
                ]).values_list('username', flat=True)
            )
        else:
            promedio = 0
            rezagados = []

        dist_estrellas = {'1_estrella': 0, '2_estrellas': 0, '3_estrellas': 0}
        for uid in estudiantes_ids:
            avg_est = ProgresoLeccion.objects.filter(
                estudiante_id=uid, completada=True
            ).aggregate(avg=Avg('estrellas'))['avg']
            if avg_est is None:
                continue
            if avg_est < 1.5:
                dist_estrellas['1_estrella'] += 1
            elif avg_est < 2.5:
                dist_estrellas['2_estrellas'] += 1
            else:
                dist_estrellas['3_estrellas'] += 1

        return {
            'tipo': 'modo_historia',
            'secciones': datos_secciones,
            'leccion_mas_errores': leccion_problematica,
            'estudiantes_rezagados': rezagados,
            'distribucion_estrellas': dist_estrellas,
        }

    def _datos_estudiante(self, profesor, estudiante_id: int | None) -> dict:
        from django.contrib.auth import get_user_model
        from apps.talleres.models import SesionTaller
        from apps.historia.models import ProgresoLeccion
        from apps.games.models import Score, LogroUsuario
        from apps.accounts.models import EstudianteProfile
        from django.db.models.functions import TruncDate

        if not estudiante_id:
            return {'sin_datos': True}

        User = get_user_model()
        try:
            estudiante = User.objects.get(pk=estudiante_id)
        except User.DoesNotExist:
            return {'sin_datos': True}

        # Verificar pertenencia al salón del profesor
        try:
            perfil_prof = profesor.profesor_profile
        except Exception:
            return {'sin_datos': True}

        if not EstudianteProfile.objects.filter(
            user=estudiante, profesor=perfil_prof
        ).exists():
            return {'sin_datos': True}

        hace_30_dias = timezone.now() - timedelta(days=30)

        sesiones = SesionTaller.objects.filter(estudiante=estudiante)
        sesiones_data = list(
            sesiones.values('taller__titulo', 'completada', 'puntos_obtenidos')
        )

        historia_data = list(
            ProgresoLeccion.objects.filter(estudiante=estudiante)
            .values('leccion__titulo', 'completada', 'estrellas')
        )

        dias_activos = (
            Score.objects.filter(user=estudiante, created_at__gte=hace_30_dias)
            .annotate(dia=TruncDate('created_at'))
            .values('dia')
            .distinct()
            .count()
        )

        logros = list(
            LogroUsuario.objects.filter(user=estudiante)
            .values_list('logro__nombre', flat=True)
        )

        # Leer perfil — cada campo por separado para evitar que un error
        # en uno reemplace datos válidos de los demás con defaults.
        try:
            perfil_est = EstudianteProfile.objects.get(user=estudiante)
            nivel = perfil_est.nivel
            puntos = perfil_est.puntos_totales
            estrellas_totales = perfil_est.total_estrellas_historia
        except EstudianteProfile.DoesNotExist:
            nivel, puntos, estrellas_totales = 1, 0, 0

        # vocabulario_desbloqueado es related_name sobre CustomUser, no EstudianteProfile
        vocab_desbloqueado = estudiante.vocabulario_desbloqueado.count()

        return {
            'tipo': 'estudiante_detalle',
            'estudiante': estudiante.get_full_name() or estudiante.username,
            'nivel': nivel,
            'puntos_totales': puntos,
            'estrellas_historia': estrellas_totales,
            'sesiones_taller': sesiones_data,
            'progreso_historia': historia_data,
            'vocabulario_desbloqueado': vocab_desbloqueado,
            'dias_activos_30d': dias_activos,
            'logros': logros,
        }
