import hashlib
import json
import logging
import time
from datetime import timedelta

import httpx
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import MensajeChat

logger = logging.getLogger(__name__)

GEMINI_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    'gemini-2.0-flash:generateContent'
)
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
MYMEMORY_URL = 'https://api.mymemory.translated.net/get'

# ── Prompts predeterminados (fallback si no hay PromptTemplate en BD) ─────────

_DEFAULT_PROMPTS = {
    'planeacion': """Eres el Asistente Milo, ayudante educativo para profesores de inglés \
en primaria colombiana que usan la plataforma NestGrow.

## Cómo funciona NestGrow

NestGrow es una plataforma donde los profesores crean **Talleres digitales** para sus estudiantes. \
Un Taller se compone de **Bloques ordenados**, y cada bloque puede ser de dos tipos:

**1. Bloque Pregunta** — una pregunta interactiva con estas variantes:
- *Opción múltiple*: el estudiante elige UNA respuesta correcta entre varias opciones
- *Casillas*: el estudiante puede elegir VARIAS respuestas correctas (todas las que apliquen)
- *Párrafo libre*: el estudiante escribe su respuesta (ideal para producción escrita)
Cada bloque pregunta tiene un puntaje parcial (por defecto 10 puntos).

**2. Bloque Minijuego** — incrusta uno de los minijuegos disponibles en la plataforma:
- 🖱️ Arrastra y Suelta — relacionar palabras con imágenes o categorías
- 🔍 Sopa de Letras — encontrar palabras escondidas
- 🧩 Rompecabezas — armar una imagen relacionada al tema
- 🎵 Juego de Audio — escuchar y relacionar sonidos con palabras
- 🎨 Juego de Pintar — colorear según instrucciones en inglés
- 🃏 Memoria — encontrar pares de palabras/imágenes
- 🦴 Ahorcado de Milo — adivinar palabras letra por letra
- ❓ Quiz Rápido — responder preguntas en tiempo límite
- 🔤 Ordenar Letras — formar palabras desorganizadas
- 🎈 Globos — elegir la respuesta correcta en globos que flotan

Los talleres otorgan **XP** (experiencia) y **Huesos** (moneda virtual de Milo) al completarse.

## Tu rol

- Planear talleres **dentro de NestGrow** con estructura de bloques lista para implementar
- Generar preguntas con sus opciones, listas para copiar directamente en la plataforma
- Sugerir qué minijuego encaja mejor con cada tema y por qué
- Ayudar con planeación de clase presencial cuando el profesor lo pida explícitamente
- Proveer vocabulario, diálogos y actividades de inglés para primaria colombiana

## Formato para planear un taller en NestGrow

Cuando te pidan planear un taller para NestGrow, usa siempre esta estructura:

---
## 🎯 Taller: [Nombre del taller]
**Tema:** [tema de inglés] | **Nivel:** [grado] | **XP sugerido:** [número] | **Huesos:** [número]

### Bloques

**Bloque 1 — Pregunta · Opción múltiple** (10 pts)
[Enunciado de la pregunta]
- A) [opción] ✅
- B) [opción]
- C) [opción]
- D) [opción]

**Bloque 2 — Minijuego · [nombre del minijuego]**
🎮 [Descripción de qué practicarán los estudiantes con este minijuego]
---

## Reglas de formato

- **Siempre responde en español**
- Usa Markdown: **negrita** para conceptos clave, ## para secciones, - para listas, emojis relevantes
- Sé conciso y práctico — el contenido debe ser implementable directamente
- Indica con ✅ la respuesta correcta en las preguntas de opción múltiple o casillas
""",

    'correccion': (
        "You are Milo, a friendly dog who helps Colombian primary school children learn English. "
        "A student answered incorrectly. "
        "Give a VERY brief correction (maximum 2 sentences) in English, friendly and encouraging. "
        "Explain why the correct answer is right using simple language for children aged 8–12. "
        "End with a very short motivating phrase. Do NOT use words like 'Error' or 'Wrong'."
    ),

    'generar_taller': (
        "Eres un experto en diseño instruccional de INGLÉS para primaria colombiana. "
        "Genera un taller de inglés completo en JSON válido según el esquema indicado. "
        "Responde ÚNICAMENTE con el objeto JSON, sin texto adicional, sin bloques de código markdown. "
        "El JSON debe ser parseable directamente.\n\n"

        "## REGLAS DE CONTENIDO (MUY IMPORTANTE)\n"
        "- El taller enseña INGLÉS: las preguntas, opciones y enunciados deben incluir vocabulario, "
        "frases o estructuras en inglés. NO hagas el taller completamente en español.\n"
        "- Formato bilingüe: instrucciones cortas en español, contenido a aprender en inglés. "
        "Ejemplo correcto: '¿Cuál es el animal correcto?' con opciones: cat, dog, car, hat.\n"
        "- Para preguntas de opción múltiple o casillas: las OPCIONES deben ser palabras o frases en inglés "
        "cuando se esté practicando vocabulario o traducción.\n"
        "- Adapta la dificultad al nivel: grado 1-2 = vocabulario básico (colores, números, animales), "
        "grado 3-4 = frases simples y oraciones, grado 5 = gramática básica y expresiones.\n\n"

        "## REGLAS DE ESTRUCTURA\n"
        "- SIEMPRE incluye bloques de MINIJUEGO si hay juegos disponibles. "
        "Distribuye los bloques: ~60%% preguntas, ~40%% minijuegos (redondeado al entero más cercano).\n"
        "- Si hay 5 bloques: al menos 2 deben ser minijuego. Si hay 3 bloques: al menos 1 minijuego.\n"
        "- Para bloques de pregunta tipo opcion_multiple o casillas: incluye exactamente 4 opciones.\n"
        "- En opcion_multiple: exactamente UNA opción es_correcta=true.\n"
        "- En casillas: pueden ser VARIAS opciones correctas.\n"
        "- Marca sugiere_imagen=true cuando la pregunta se beneficia de imagen de apoyo visual.\n"
        "- Marca sugiere_video=true solo si el bloque necesita escuchar audio o ver algo.\n"
        "- Para bloques tipo 'parrafo': no incluyas el campo 'opciones'.\n\n"

        "## TIPOS DE MINIJUEGO DISPONIBLES Y CUÁNDO USARLOS\n"
        "- drag_and_drop: relacionar palabras en inglés con imágenes o categorías → ideal para vocabulario nuevo\n"
        "- word_search: sopa de letras con palabras en inglés → ideal para repasar vocabulario\n"
        "- puzzle: armar imagen relacionada al tema → ideal como actividad de cierre lúdica\n"
        "- audio_matching: escuchar y relacionar sonidos con palabras → ideal para pronunciación\n"
        "- painting: colorear según instrucciones en inglés → ideal para grados 1-2\n"
        "- memoria: encontrar pares de palabras/imágenes → ideal para vocabulario\n"
        "- ahorcado: adivinar palabras en inglés letra por letra → ideal para repasar palabras conocidas\n"
        "- quiz: preguntas rápidas con tiempo → ideal para evaluación rápida\n"
        "- ordenar_letras: formar palabras en inglés desorganizadas → ideal para ortografía\n"
        "- globos: elegir respuesta correcta en globos → ideal como actividad motivadora\n"
        "- comparacion: comparar pares de imágenes → ideal para descripciones\n"
    ),

    'insights_periodo': (
        "Eres un analista educativo experto. Analiza los datos de rendimiento de un período escolar "
        "y genera un informe ejecutivo en español. "
        "Sé concreto, usa datos específicos del JSON, identifica patrones, menciona nombres reales si los hay. "
        "Estructura tu respuesta en: (1) Resumen ejecutivo (2-3 oraciones), "
        "(2) Fortalezas del grupo (2 puntos), (3) Áreas de mejora (2-3 puntos con recomendaciones prácticas), "
        "(4) Estudiantes que requieren atención especial si los hay. "
        "Tono profesional pero cálido, orientado a acción docente inmediata."
    ),
}


def _get_prompt(nombre: str) -> str:
    """Retorna el system prompt: intenta BD primero, fallback a hardcoded."""
    from .models import PromptTemplate
    try:
        pt = PromptTemplate.objects.get(nombre=nombre, activo=True)
        return pt.system
    except Exception:
        return _DEFAULT_PROMPTS.get(nombre, '')


def _cache_key(messages: list, system: str) -> str:
    raw = json.dumps({'m': messages, 's': system}, ensure_ascii=False, sort_keys=True)
    return 'ia_' + hashlib.sha256(raw.encode()).hexdigest()


def _log_llamada(motor: str, proposito: str, latencia_ms: int,
                 exito: bool = True, cache_hit: bool = False,
                 usuario=None) -> None:
    """Registra una llamada (o cache hit) en LlamadaIA de forma silenciosa."""
    try:
        from .models import LlamadaIA
        LlamadaIA.objects.create(
            motor=motor,
            proposito=proposito,
            latencia_ms=latencia_ms,
            exito=exito,
            cache_hit=cache_hit,
            usuario=usuario,
        )
    except Exception as exc:
        logger.warning('No se pudo registrar LlamadaIA: %s', exc)


# ── Traducción con MyMemory ────────────────────────────────────────────────────

def traducir_mymemory(texto: str, origen: str = 'es', destino: str = 'en') -> str | None:
    """
    Traduce `texto` usando MyMemory. Retorna la traducción o None si falla.
    Almacena el resultado en caché por 30 días.
    """
    if not texto or not texto.strip():
        return None

    cache_k = 'trans_' + hashlib.md5(f'{origen}|{destino}|{texto}'.encode()).hexdigest()
    cached = cache.get(cache_k)
    if cached:
        return cached

    params: dict = {'q': texto.strip(), 'langpair': f'{origen}|{destino}'}
    api_key = getattr(settings, 'MYMEMORY_API_KEY', '')
    if api_key:
        params['key'] = api_key

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(MYMEMORY_URL, params=params)
        if resp.status_code == 200:
            data = resp.json()
            traduccion = data.get('responseData', {}).get('translatedText', '')
            if traduccion and traduccion.upper() != texto.upper():
                cache.set(cache_k, traduccion, 60 * 60 * 24 * 30)
                return traduccion
    except Exception as exc:
        logger.warning('MyMemory falló: %s', exc)
    return None


class AsistenteMilo:

    # ── IA core ───────────────────────────────────────────────────────────────

    async def _llamar_ia(
        self,
        messages: list[dict],
        system_prompt: str,
        json_mode: bool = False,
        proposito: str = '',
        usuario=None,
        ttl: int = 86400,
    ) -> dict:
        """
        Intenta Gemini, fallback Groq.
        - Cachea la respuesta por `ttl` segundos (0 = sin caché).
        - Registra en LlamadaIA.
        - Si json_mode=True activa JSON mode en ambos proveedores.
        Retorna {'texto': ..., 'motor': ...}
        """
        from asgiref.sync import sync_to_async

        ck = _cache_key(messages, system_prompt) if ttl > 0 else None

        # Intento desde caché
        if ck:
            cached = cache.get(ck)
            if cached:
                await sync_to_async(_log_llamada)(
                    'cache', proposito, 0, True, True, usuario
                )
                return {'texto': cached, 'motor': 'cache'}

        t0 = time.monotonic()

        try:
            resultado = await self._gemini(messages, system_prompt, json_mode=json_mode)
            if resultado:
                latencia = int((time.monotonic() - t0) * 1000)
                await sync_to_async(_log_llamada)('gemini', proposito, latencia, True, False, usuario)
                if ck:
                    cache.set(ck, resultado, ttl)
                return {'texto': resultado, 'motor': 'gemini'}
        except Exception as exc:
            logger.warning('Gemini falló: %s', exc)

        try:
            resultado = await self._groq(messages, system_prompt, json_mode=json_mode)
            if resultado:
                latencia = int((time.monotonic() - t0) * 1000)
                await sync_to_async(_log_llamada)('groq', proposito, latencia, True, False, usuario)
                if ck:
                    cache.set(ck, resultado, ttl)
                return {'texto': resultado, 'motor': 'groq'}
        except Exception as exc:
            logger.warning('Groq falló: %s', exc)

        latencia = int((time.monotonic() - t0) * 1000)
        await sync_to_async(_log_llamada)('error', proposito, latencia, False, False, usuario)
        return {
            'texto': 'El asistente no está disponible en este momento. Intenta más tarde.',
            'motor': 'error',
        }

    async def _gemini(
        self, messages: list[dict], system_prompt: str, json_mode: bool = False
    ) -> str | None:
        contents = []
        for m in messages:
            role = 'user' if m['role'] == 'user' else 'model'
            contents.append({'role': role, 'parts': [{'text': m['content']}]})

        gen_config: dict = {'maxOutputTokens': 2048, 'temperature': 0.7}
        if json_mode:
            gen_config['responseMimeType'] = 'application/json'

        payload = {
            'system_instruction': {'parts': [{'text': system_prompt}]},
            'contents': contents,
            'generationConfig': gen_config,
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

    async def _groq(
        self, messages: list[dict], system_prompt: str, json_mode: bool = False
    ) -> str | None:
        groq_messages = [{'role': 'system', 'content': system_prompt}] + messages
        payload: dict = {
            'model': 'llama-3.3-70b-versatile',
            'messages': groq_messages,
            'max_tokens': 2048,
            'temperature': 0.7,
        }
        if json_mode:
            payload['response_format'] = {'type': 'json_object'}

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

        system = _get_prompt('planeacion')
        # Chat de planeación: caché 1h (respuestas conversacionales varían mucho)
        resultado = await self._llamar_ia(
            messages, system, proposito='chat_planeacion',
            usuario=profesor, ttl=3600,
        )

        await sync_to_async(MensajeChat.objects.create)(
            profesor=profesor, rol='user',
            contenido=mensaje_usuario, modo='planeacion',
        )
        await sync_to_async(MensajeChat.objects.create)(
            profesor=profesor, rol='assistant',
            contenido=resultado['texto'], modo='planeacion',
            motor_usado=resultado['motor'] if resultado['motor'] != 'cache' else 'gemini',
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
        return await self._llamar_ia(
            messages, system_prompt,
            proposito=f'analizar_{tipo_analisis}',
            usuario=profesor,
            ttl=3600 * 6,  # 6h de caché para análisis
        )

    # ── Generador de talleres con IA (M1) ─────────────────────────────────────

    async def generar_taller(
        self,
        profesor,
        tema: str,
        nivel: str,
        num_bloques: int,
        juegos_disponibles: list[dict],
    ) -> dict:
        """
        Genera un taller completo en JSON.
        `juegos_disponibles` es lista de {'id': pk, 'nombre': str}.
        Retorna {'taller': dict, 'motor': str} o {'error': str}.
        """
        juegos_str = ', '.join(
            f"id={j['id']} ({j['nombre']})" for j in juegos_disponibles
        ) or 'ninguno disponible'

        schema_ejemplo = {
            "titulo": "Nombre del taller",
            "descripcion": "Descripción breve del taller",
            "puntos_xp": 20,
            "huesos_recompensa": 10,
            "bloques": [
                {
                    "tipo": "pregunta",
                    "enunciado": "Texto de la pregunta",
                    "tipo_respuesta": "opcion_multiple",
                    "puntaje_parcial": 10,
                    "sugiere_imagen": True,
                    "nota_imagen": "Descripción de qué imagen sería útil aquí",
                    "sugiere_video": False,
                    "opciones": [
                        {"texto": "opción 1", "es_correcta": True},
                        {"texto": "opción 2", "es_correcta": False},
                        {"texto": "opción 3", "es_correcta": False},
                        {"texto": "opción 4", "es_correcta": False},
                    ]
                },
                {
                    "tipo": "minijuego",
                    "game_id": 1,
                    "instruccion_extra": "Descripción breve de lo que practicará el estudiante"
                }
            ]
        }

        # 5-6 bloques → 1 minijuego; 7+ bloques → 2 minijuegos
        num_minis_requeridos = (1 if num_bloques < 7 else 2) if juegos_disponibles else 0
        num_preguntas = num_bloques - num_minis_requeridos

        if juegos_disponibles:
            instruccion_minis = (
                f"OBLIGATORIO: incluye EXACTAMENTE {num_minis_requeridos} bloque(s) de tipo 'minijuego' "
                f"y {num_preguntas} bloque(s) de tipo 'pregunta'. "
                f"Elige el tipo de minijuego más apropiado para el tema según las descripciones del sistema. "
                f"Juegos disponibles (usa el game_id exacto): {juegos_str}."
            )
        else:
            instruccion_minis = (
                "No hay juegos disponibles, usa solo bloques de tipo 'pregunta'."
            )

        prompt = (
            f"Crea un taller de inglés para {nivel} sobre el tema: '{tema}'.\n"
            f"Total de bloques: {num_bloques}.\n"
            f"{instruccion_minis}\n"
            f"Recuerda: el contenido DEBE incluir inglés (vocabulario, frases u opciones en inglés). "
            f"Usa instrucciones cortas en español pero el contenido a aprender en inglés.\n"
            f"Varía los tipos de pregunta: opcion_multiple, casillas y parrafo.\n"
            f"Para 'parrafo' no incluyas el campo 'opciones'.\n\n"
            f"Devuelve ÚNICAMENTE este JSON (sin texto adicional):\n"
            f"{json.dumps(schema_ejemplo, ensure_ascii=False, indent=2)}"
        )

        system = _get_prompt('generar_taller')
        messages = [{'role': 'user', 'content': prompt}]

        resultado = await self._llamar_ia(
            messages, system,
            json_mode=True,
            proposito='generar_taller',
            usuario=profesor,
            ttl=0,  # No cachear — cada generación debe ser única
        )

        if resultado['motor'] == 'error':
            return {'error': resultado['texto']}

        try:
            texto = resultado['texto'].strip()
            # Limpiar bloques de código markdown si el modelo los incluye
            if texto.startswith('```'):
                texto = texto.split('```', 2)[1]
                if texto.startswith('json'):
                    texto = texto[4:]
                texto = texto.rsplit('```', 1)[0]
            taller_data = json.loads(texto)
            return {'taller': taller_data, 'motor': resultado['motor']}
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            logger.warning('Error parseando JSON de generar_taller: %s | Respuesta: %s', exc, resultado['texto'][:500])
            return {'error': 'La IA devolvió una respuesta que no se pudo procesar. Intenta de nuevo.'}

    # ── Insights de período (M3) ──────────────────────────────────────────────

    async def generar_insights_periodo(self, profesor, periodo) -> dict:
        """
        Genera un análisis textual del período con datos reales.
        Retorna {'texto': str, 'motor': str}.
        """
        from asgiref.sync import sync_to_async
        datos = await sync_to_async(self._datos_periodo)(profesor, periodo)

        if datos.get('sin_datos'):
            return {
                'texto': 'Aún no hay datos suficientes en este período para generar un análisis.',
                'motor': 'sin_datos',
            }

        system = _get_prompt('insights_periodo')
        messages = [
            {
                'role': 'user',
                'content': (
                    f'Analiza el siguiente período escolar y genera el informe ejecutivo.\n'
                    f'Datos: {json.dumps(datos, ensure_ascii=False, default=str)}'
                ),
            }
        ]
        return await self._llamar_ia(
            messages, system,
            proposito='insights_periodo',
            usuario=profesor,
            ttl=3600 * 3,  # 3h de caché
        )

    def _datos_periodo(self, profesor, periodo) -> dict:
        """Recolecta datos del período para el análisis."""
        from apps.talleres.models import (
            AsignacionTaller, AsignacionMinijuego,
            SesionTaller, RegistroMinijuegoPeriodo,
        )
        from django.db.models import Avg, Count
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Misma query que resultados_periodo: estudiantes cuyo perfil apunta al salón del período
        estudiantes_ids = list(
            User.objects.filter(
                estudiante_profile__salon=periodo.salon,
                role='estudiante',
            ).values_list('id', flat=True)
        )
        if not estudiantes_ids:
            return {'sin_datos': True}

        total_estudiantes = len(estudiantes_ids)

        # ── Talleres ──
        talleres_asig = list(AsignacionTaller.objects.filter(periodo=periodo).select_related('taller'))
        datos_talleres = []
        for asig in talleres_asig:
            sesiones = SesionTaller.objects.filter(
                taller=asig.taller, estudiante_id__in=estudiantes_ids
            )
            completadas = sesiones.filter(completada=True)
            avg = completadas.aggregate(avg=Avg('puntos_obtenidos'))['avg'] or 0
            posibles = asig.taller.total_puntos_posibles() or 1
            datos_talleres.append({
                'taller': asig.taller.titulo,
                'completaron': completadas.count(),
                'total_estudiantes': total_estudiantes,
                'promedio_pct': round((avg / posibles) * 100, 1) if posibles else 0,
            })

        # ── Minijuegos ──
        mini_asig = list(AsignacionMinijuego.objects.filter(periodo=periodo).select_related('game'))
        datos_minis = []
        for asig in mini_asig:
            registros = RegistroMinijuegoPeriodo.objects.filter(
                asignacion=asig, estudiante_id__in=estudiantes_ids
            )
            completados = registros.filter(completado=True)
            avg_pct = (
                sum(r.porcentaje for r in completados) / completados.count()
                if completados.count() > 0 else 0
            )
            datos_minis.append({
                'juego': asig.game.title,
                'completaron': completados.count(),
                'total_estudiantes': total_estudiantes,
                'promedio_pct': round(avg_pct, 1),
            })

        # ── Estudiantes en riesgo ──
        en_riesgo = []
        for uid in estudiantes_ids:
            sesiones_est = SesionTaller.objects.filter(
                taller__in=[a.taller for a in talleres_asig],
                estudiante_id=uid, completada=True,
            )
            completadas_est = sesiones_est.count()
            total_asig = len(talleres_asig)
            if total_asig > 0 and completadas_est < total_asig * 0.5:
                try:
                    nombre = User.objects.get(pk=uid).get_full_name() or User.objects.get(pk=uid).username
                    en_riesgo.append(nombre)
                except Exception:
                    pass

        return {
            'periodo': periodo.titulo,
            'salon': str(periodo.salon),
            'fecha_inicio': str(periodo.fecha_inicio),
            'fecha_fin': str(periodo.fecha_fin),
            'total_estudiantes': total_estudiantes,
            'talleres': datos_talleres,
            'minijuegos': datos_minis,
            'estudiantes_en_riesgo': en_riesgo,
        }

    # ── Recolección de datos (análisis general) ───────────────────────────────

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

        try:
            perfil_est = EstudianteProfile.objects.get(user=estudiante)
            nivel = perfil_est.nivel
            puntos = perfil_est.puntos_totales
            estrellas_totales = perfil_est.total_estrellas_historia
        except EstudianteProfile.DoesNotExist:
            nivel, puntos, estrellas_totales = 1, 0, 0

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
