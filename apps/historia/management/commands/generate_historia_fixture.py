"""
Management command: generate_historia_fixture
Generates apps/historia/fixtures/modo_historia.json with 10 sections,
51 lessons, and ~387 activities for the Historia story mode.
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

SECCIONES = [
    {"pk": 1, "titulo": "Los Colores del Mundo", "descripcion": "Aprende los colores básicos y cómo describirlos en inglés.", "orden": 1, "icono_emoji": "🎨", "color_hex": "#FF6B6B", "is_desbloqueada_por_defecto": True},
    {"pk": 2, "titulo": "Mi Familia y Yo", "descripcion": "Presenta a los miembros de tu familia en inglés.", "orden": 2, "icono_emoji": "👨‍👩‍👧‍👦", "color_hex": "#FF9F43"},
    {"pk": 3, "titulo": "Los Números Mágicos", "descripcion": "Cuenta, suma y describe cantidades en inglés.", "orden": 3, "icono_emoji": "🔢", "color_hex": "#FECA57"},
    {"pk": 4, "titulo": "Animales del Mundo", "descripcion": "Conoce los animales y sus sonidos en inglés.", "orden": 4, "icono_emoji": "🦁", "color_hex": "#48DBFB"},
    {"pk": 5, "titulo": "Mi Cuerpo", "descripcion": "Nombra las partes del cuerpo y habla de cómo te sientes.", "orden": 5, "icono_emoji": "🧍", "color_hex": "#FF9FF3"},
    {"pk": 6, "titulo": "La Comida Rica", "descripcion": "Descubre cómo pedir y describir comidas en inglés.", "orden": 6, "icono_emoji": "🍎", "color_hex": "#54A0FF"},
    {"pk": 7, "titulo": "Mi Casa y mis Cosas", "descripcion": "Describe los lugares y objetos de tu hogar.", "orden": 7, "icono_emoji": "🏠", "color_hex": "#5F27CD"},
    {"pk": 8, "titulo": "El Tiempo y las Estaciones", "descripcion": "Habla del clima y los cambios del año.", "orden": 8, "icono_emoji": "☀️", "color_hex": "#00D2D3"},
    {"pk": 9, "titulo": "Mis Actividades Favoritas", "descripcion": "Describe lo que te gusta hacer en tu tiempo libre.", "orden": 9, "icono_emoji": "⚽", "color_hex": "#FF9F43"},
    {"pk": 10, "titulo": "Mi Pueblo, Mi Mundo", "descripcion": "Habla de los lugares de tu comunidad y cómo ir a ellos.", "orden": 10, "icono_emoji": "🗺️", "color_hex": "#6C63FF"},
]

# Each section: list of lesson dicts. Keys: titulo, descripcion_corta, icono_emoji, puntos_xp, huesos_recompensa, tiempo_estimado_minutos, is_repaso
LECCIONES_POR_SECCION = {
    1: [
        {"titulo": "Colores Primarios", "descripcion_corta": "Red, blue and yellow — the building blocks.", "icono_emoji": "🔴", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Colores Secundarios", "descripcion_corta": "Mix two colors and get something new!", "icono_emoji": "🟠", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Colores Oscuros y Claros", "descripcion_corta": "Dark and light shades of color.", "icono_emoji": "⚫", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "¿De qué color es?", "descripcion_corta": "Ask and answer about object colors.", "icono_emoji": "🎨", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Los Colores", "descripcion_corta": "Review everything you learned about colors!", "icono_emoji": "🌈", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    2: [
        {"titulo": "Papá y Mamá", "descripcion_corta": "Father, mother and immediate family.", "icono_emoji": "👨‍👩‍👧", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Hermanos y Hermanas", "descripcion_corta": "Brother, sister and siblings.", "icono_emoji": "👦", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Abuelos y Tíos", "descripcion_corta": "Grandparents, aunts, uncles and cousins.", "icono_emoji": "👴", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "This is my family", "descripcion_corta": "Present your family in English.", "icono_emoji": "📸", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Mi Familia", "descripcion_corta": "Review family vocabulary and expressions.", "icono_emoji": "👨‍👩‍👧‍👦", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    3: [
        {"titulo": "Del 1 al 10", "descripcion_corta": "Count from one to ten.", "icono_emoji": "🔢", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Del 11 al 20", "descripcion_corta": "Count from eleven to twenty.", "icono_emoji": "2️⃣", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Decenas: 10, 20, 30...", "descripcion_corta": "Ten, twenty, thirty and multiples of ten.", "icono_emoji": "💯", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "¿Cuántos hay?", "descripcion_corta": "Ask and answer 'How many?' questions.", "icono_emoji": "🍎", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Números Ordinales", "descripcion_corta": "First, second, third — order matters!", "icono_emoji": "🥇", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Los Números", "descripcion_corta": "Review all number concepts.", "icono_emoji": "➕", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    4: [
        {"titulo": "Animales de la Granja", "descripcion_corta": "Cow, pig, horse, chicken and more.", "icono_emoji": "🐄", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Animales de la Selva", "descripcion_corta": "Lion, elephant, monkey and jungle animals.", "icono_emoji": "🦁", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Animales del Mar", "descripcion_corta": "Fish, shark, dolphin and ocean animals.", "icono_emoji": "🐟", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Sonidos de Animales", "descripcion_corta": "What sound does each animal make?", "icono_emoji": "🔊", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Los Animales", "descripcion_corta": "Review all animal vocabulary.", "icono_emoji": "🦓", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    5: [
        {"titulo": "La Cabeza", "descripcion_corta": "Head, eyes, ears, nose and mouth.", "icono_emoji": "👁️", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "El Cuerpo", "descripcion_corta": "Arms, hands, legs, feet and body parts.", "icono_emoji": "💪", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "¿Cómo te sientes?", "descripcion_corta": "Happy, sad, tired, hungry — how do you feel?", "icono_emoji": "😊", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Me duele...", "descripcion_corta": "Describe aches and pains in English.", "icono_emoji": "🤒", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Mi Cuerpo", "descripcion_corta": "Review body parts and feelings.", "icono_emoji": "🧍", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    6: [
        {"titulo": "Frutas y Verduras", "descripcion_corta": "Apple, banana, carrot, tomato and more.", "icono_emoji": "🍎", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Desayuno", "descripcion_corta": "Breakfast foods: eggs, bread, milk, cereal.", "icono_emoji": "🥞", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Almuerzo y Cena", "descripcion_corta": "Lunch and dinner vocabulary.", "icono_emoji": "🍽️", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Me gusta / No me gusta", "descripcion_corta": "I like / I don't like — food preferences.", "icono_emoji": "😋", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "En el Restaurante", "descripcion_corta": "Order food at a restaurant in English.", "icono_emoji": "🍔", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: La Comida", "descripcion_corta": "Review all food vocabulary and expressions.", "icono_emoji": "🍴", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    7: [
        {"titulo": "Cuartos de la Casa", "descripcion_corta": "Living room, bedroom, kitchen, bathroom.", "icono_emoji": "🛋️", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Muebles y Objetos", "descripcion_corta": "Table, chair, bed, lamp and home objects.", "icono_emoji": "🪑", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "¿Dónde está?", "descripcion_corta": "In, on, under, next to — prepositions of place.", "icono_emoji": "📍", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Mi Habitación", "descripcion_corta": "Describe your own bedroom in English.", "icono_emoji": "🛏️", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Mi Casa", "descripcion_corta": "Review home vocabulary and prepositions.", "icono_emoji": "🏠", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    8: [
        {"titulo": "El Tiempo Hoy", "descripcion_corta": "Sunny, cloudy, rainy, windy — today's weather.", "icono_emoji": "⛅", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Las Cuatro Estaciones", "descripcion_corta": "Spring, summer, fall and winter.", "icono_emoji": "🍂", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "¿Qué ropa usar?", "descripcion_corta": "Dress for the weather — clothes vocabulary.", "icono_emoji": "🧥", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Los Meses del Año", "descripcion_corta": "January through December.", "icono_emoji": "📅", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: El Tiempo", "descripcion_corta": "Review weather, seasons and months.", "icono_emoji": "🌡️", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    9: [
        {"titulo": "Deportes", "descripcion_corta": "Soccer, basketball, swimming and more sports.", "icono_emoji": "⚽", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Hobbies", "descripcion_corta": "Reading, drawing, dancing, playing video games.", "icono_emoji": "🎮", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Días de la Semana", "descripcion_corta": "Monday through Sunday and daily routines.", "icono_emoji": "📆", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "¿Qué haces después del colegio?", "descripcion_corta": "Describe your after-school activities.", "icono_emoji": "🎒", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Repaso: Actividades", "descripcion_corta": "Review all activities and daily routine vocabulary.", "icono_emoji": "🏃", "puntos_xp": 25, "huesos_recompensa": 5, "tiempo_estimado_minutos": 18, "is_repaso": True},
    ],
    10: [
        {"titulo": "Lugares del Pueblo", "descripcion_corta": "School, park, market, hospital, church.", "icono_emoji": "🏫", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "¿Cómo llego?", "descripcion_corta": "Turn left, turn right, go straight — giving directions.", "icono_emoji": "🗺️", "puntos_xp": 15, "huesos_recompensa": 3, "tiempo_estimado_minutos": 12},
        {"titulo": "Transporte", "descripcion_corta": "Bus, car, bicycle, motorcycle and transport.", "icono_emoji": "🚌", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "Mi Comunidad", "descripcion_corta": "Describe your neighborhood and community.", "icono_emoji": "🏘️", "puntos_xp": 20, "huesos_recompensa": 4, "tiempo_estimado_minutos": 14},
        {"titulo": "¡Gran Repaso Final!", "descripcion_corta": "Review everything from the whole journey!", "icono_emoji": "🏆", "puntos_xp": 30, "huesos_recompensa": 8, "tiempo_estimado_minutos": 25, "is_repaso": True},
    ],
}

# Activity content definitions keyed by (seccion_pk, leccion_orden, tipo)
# For brevity we use a helper that generates sensible content per tipo/tema
def make_actividades(tema_es, tema_en, vocabulario, seccion_titulo,
                     seccion_pk=1, leccion_global_idx=0, dificultad=1,
                     is_repaso=False):
    """
    Returns a list of activity dicts (sin pk/leccion, those assigned later).
    vocabulario: list of {"es": str, "en": str} dicts (at least 6)
    """
    v = vocabulario  # shorthand
    pairs_6 = v[:6]

    actividades = [
        {
            "orden": 1,
            "tipo": "introduccion",
            "puntos_actividad": 0,
            "datos": {
                "titulo": f"¡Bienvenido a {tema_es}!",
                "texto": f"En esta lección aprenderás palabras sobre {tema_es.lower()} en inglés. ¡Milo te acompañará en todo el camino!",
                "imagen_url": f"/historia/img/{tema_en.lower().replace(' ', '_')}_intro.png",
                "palabras_clave": [{"es": w["es"], "en": w["en"]} for w in v[:4]],
            },
        },
        {
            "orden": 2,
            "tipo": "vocabulario",
            "puntos_actividad": 0,
            "datos": {
                "titulo": f"Palabras de {tema_es}",
                "tarjetas": [{"es": w["es"], "en": w["en"], "emoji": w.get("emoji", "📝")} for w in v],
            },
        },
        {
            "orden": 3,
            "tipo": "dialogo",
            "puntos_actividad": 0,
            "datos": {
                "titulo": "Mini-diálogo",
                "lineas": [
                    {"personaje": "Milo", "texto": f"Hi! Do you know how to say '{v[0]['es']}' in English?", "avatar": "🐕"},
                    {"personaje": "Tú", "texto": f"Yes! It's '{v[0]['en']}'!", "avatar": "👦"},
                    {"personaje": "Milo", "texto": f"Great! And '{v[1]['es']}'?", "avatar": "🐕"},
                    {"personaje": "Tú", "texto": f"That's '{v[1]['en']}'!", "avatar": "👦"},
                    {"personaje": "Milo", "texto": "You're doing amazing! Let's keep going!", "avatar": "🐕"},
                ],
            },
        },
        {
            "orden": 4,
            "tipo": "listening",
            "puntos_actividad": 2,
            "datos": {
                "titulo": "¿Qué escuchas?",
                "instruccion": "Listen and select the correct word.",
                "preguntas": [
                    {
                        "audio_texto": w["en"],
                        "opciones": [w["en"]] + [v[(i+1) % len(v)]["en"], v[(i+2) % len(v)]["en"]],
                        "respuesta_correcta": w["en"],
                    }
                    for i, w in enumerate(pairs_6[:4])
                ],
            },
        },
        {
            "orden": 5,
            "tipo": "pronunciacion",
            "puntos_actividad": 1,
            "datos": {
                "titulo": "Practica tu pronunciación",
                "instruccion": "Repeat each word clearly after Milo.",
                "palabras": [{"en": w["en"], "es": w["es"]} for w in v[:5]],
            },
        },
        {
            "orden": 6,
            "tipo": "reading",
            "puntos_actividad": 2,
            "datos": {
                "titulo": "Lee y responde",
                "texto": _make_reading_text(tema_es, tema_en, v),
                "preguntas": [
                    {
                        "pregunta": f"What is the English word for '{v[0]['es']}'?",
                        "opciones": [v[0]["en"], v[1]["en"], v[2]["en"]],
                        "respuesta_correcta": v[0]["en"],
                    },
                    {
                        "pregunta": f"What is the English word for '{v[1]['es']}'?",
                        "opciones": [v[0]["en"], v[1]["en"], v[2]["en"]],
                        "respuesta_correcta": v[1]["en"],
                    },
                ],
            },
        },
        {
            "orden": 7,
            "tipo": "writing",
            "puntos_actividad": 2,
            "datos": {
                "titulo": "Escribe en inglés",
                "instruccion": "Type the English word for each picture.",
                "ejercicios": [
                    {"es": w["es"], "en": w["en"], "emoji": w.get("emoji", "📝")}
                    for w in v[:4]
                ],
            },
        },
        _make_minijuego_embed(seccion_pk, leccion_global_idx, v, dificultad),
    ]

    if is_repaso:
        # Replace activities 3 (dialogo) with a more challenging quiz, keep rest
        actividades[2] = {
            "orden": 3,
            "tipo": "reading",
            "puntos_actividad": 2,
            "datos": {
                "titulo": "Repaso de Lectura",
                "texto": f"Let's review {tema_es.lower()}! We learned many new words. Do you remember them all?",
                "preguntas": [
                    {
                        "pregunta": f"How do you say '{v[i]['es']}' in English?",
                        "opciones": [v[i]["en"], v[(i+1) % len(v)]["en"], v[(i+2) % len(v)]["en"]],
                        "respuesta_correcta": v[i]["en"],
                    }
                    for i in range(3)
                ],
            },
        }

    return actividades


def _make_reading_text(tema_es, tema_en, vocabulario):
    v = vocabulario
    words = [w["en"] for w in v[:4]]
    return (
        f"In English, we use many words for {tema_en.lower()}. "
        f"For example, '{words[0]}' and '{words[1]}' are very common words. "
        f"We can also say '{words[2]}' and '{words[3]}'. "
        f"Learning {tema_en.lower()} vocabulary is fun and useful!"
    )


# ── Vocabulary per section/lesson ────────────────────────────────────────────

VOCABULARIO = {
    # Sección 1 — Colores
    (1, 1): [  # Colores Primarios
        {"es": "rojo", "en": "red", "emoji": "🔴"},
        {"es": "azul", "en": "blue", "emoji": "🔵"},
        {"es": "amarillo", "en": "yellow", "emoji": "🟡"},
        {"es": "color", "en": "color", "emoji": "🎨"},
        {"es": "claro", "en": "light", "emoji": "🌟"},
        {"es": "oscuro", "en": "dark", "emoji": "🌑"},
    ],
    (1, 2): [  # Colores Secundarios
        {"es": "verde", "en": "green", "emoji": "🟢"},
        {"es": "naranja", "en": "orange", "emoji": "🟠"},
        {"es": "morado", "en": "purple", "emoji": "🟣"},
        {"es": "mezclar", "en": "mix", "emoji": "🎨"},
        {"es": "pintar", "en": "paint", "emoji": "🖌️"},
        {"es": "brillante", "en": "bright", "emoji": "✨"},
    ],
    (1, 3): [  # Colores Oscuros y Claros
        {"es": "negro", "en": "black", "emoji": "⚫"},
        {"es": "blanco", "en": "white", "emoji": "⚪"},
        {"es": "gris", "en": "gray", "emoji": "🩶"},
        {"es": "rosado", "en": "pink", "emoji": "🌸"},
        {"es": "café/marrón", "en": "brown", "emoji": "🟤"},
        {"es": "plateado", "en": "silver", "emoji": "🪙"},
    ],
    (1, 4): [  # ¿De qué color es?
        {"es": "¿De qué color es?", "en": "What color is it?", "emoji": "❓"},
        {"es": "Es...", "en": "It is...", "emoji": "👉"},
        {"es": "cielo", "en": "sky", "emoji": "🌤️"},
        {"es": "hierba", "en": "grass", "emoji": "🌿"},
        {"es": "sol", "en": "sun", "emoji": "☀️"},
        {"es": "noche", "en": "night", "emoji": "🌙"},
    ],
    (1, 5): [  # Repaso Colores
        {"es": "rojo", "en": "red", "emoji": "🔴"},
        {"es": "azul", "en": "blue", "emoji": "🔵"},
        {"es": "verde", "en": "green", "emoji": "🟢"},
        {"es": "amarillo", "en": "yellow", "emoji": "🟡"},
        {"es": "naranja", "en": "orange", "emoji": "🟠"},
        {"es": "morado", "en": "purple", "emoji": "🟣"},
    ],
    # Sección 2 — Familia
    (2, 1): [
        {"es": "papá", "en": "father", "emoji": "👨"},
        {"es": "mamá", "en": "mother", "emoji": "👩"},
        {"es": "familia", "en": "family", "emoji": "👨‍👩‍👧"},
        {"es": "padres", "en": "parents", "emoji": "👫"},
        {"es": "hijo", "en": "son", "emoji": "👦"},
        {"es": "hija", "en": "daughter", "emoji": "👧"},
    ],
    (2, 2): [
        {"es": "hermano", "en": "brother", "emoji": "👦"},
        {"es": "hermana", "en": "sister", "emoji": "👧"},
        {"es": "hermanos", "en": "siblings", "emoji": "👫"},
        {"es": "mayor", "en": "older", "emoji": "⬆️"},
        {"es": "menor", "en": "younger", "emoji": "⬇️"},
        {"es": "gemelos", "en": "twins", "emoji": "👯"},
    ],
    (2, 3): [
        {"es": "abuelo", "en": "grandfather", "emoji": "👴"},
        {"es": "abuela", "en": "grandmother", "emoji": "👵"},
        {"es": "tío", "en": "uncle", "emoji": "👨"},
        {"es": "tía", "en": "aunt", "emoji": "👩"},
        {"es": "primo/prima", "en": "cousin", "emoji": "🧑"},
        {"es": "sobrino/sobrina", "en": "nephew/niece", "emoji": "👶"},
    ],
    (2, 4): [
        {"es": "Esta es mi familia", "en": "This is my family", "emoji": "📸"},
        {"es": "Él es mi...", "en": "He is my...", "emoji": "👨"},
        {"es": "Ella es mi...", "en": "She is my...", "emoji": "👩"},
        {"es": "Ellos son mis...", "en": "They are my...", "emoji": "👨‍👩‍👧"},
        {"es": "Tengo... hermanos", "en": "I have... siblings", "emoji": "🔢"},
        {"es": "Mi familia es grande", "en": "My family is big", "emoji": "🏠"},
    ],
    (2, 5): [
        {"es": "papá", "en": "father", "emoji": "👨"},
        {"es": "mamá", "en": "mother", "emoji": "👩"},
        {"es": "hermano", "en": "brother", "emoji": "👦"},
        {"es": "hermana", "en": "sister", "emoji": "👧"},
        {"es": "abuelo", "en": "grandfather", "emoji": "👴"},
        {"es": "abuela", "en": "grandmother", "emoji": "👵"},
    ],
    # Sección 3 — Números
    (3, 1): [
        {"es": "uno", "en": "one", "emoji": "1️⃣"},
        {"es": "dos", "en": "two", "emoji": "2️⃣"},
        {"es": "tres", "en": "three", "emoji": "3️⃣"},
        {"es": "cuatro", "en": "four", "emoji": "4️⃣"},
        {"es": "cinco", "en": "five", "emoji": "5️⃣"},
        {"es": "diez", "en": "ten", "emoji": "🔟"},
    ],
    (3, 2): [
        {"es": "once", "en": "eleven", "emoji": "1️⃣1️⃣"},
        {"es": "doce", "en": "twelve", "emoji": "1️⃣2️⃣"},
        {"es": "trece", "en": "thirteen", "emoji": "1️⃣3️⃣"},
        {"es": "catorce", "en": "fourteen", "emoji": "1️⃣4️⃣"},
        {"es": "quince", "en": "fifteen", "emoji": "1️⃣5️⃣"},
        {"es": "veinte", "en": "twenty", "emoji": "2️⃣0️⃣"},
    ],
    (3, 3): [
        {"es": "diez", "en": "ten", "emoji": "🔟"},
        {"es": "veinte", "en": "twenty", "emoji": "2️⃣0️⃣"},
        {"es": "treinta", "en": "thirty", "emoji": "3️⃣0️⃣"},
        {"es": "cuarenta", "en": "forty", "emoji": "4️⃣0️⃣"},
        {"es": "cincuenta", "en": "fifty", "emoji": "5️⃣0️⃣"},
        {"es": "cien", "en": "one hundred", "emoji": "💯"},
    ],
    (3, 4): [
        {"es": "¿Cuántos hay?", "en": "How many are there?", "emoji": "❓"},
        {"es": "Hay...", "en": "There are...", "emoji": "👉"},
        {"es": "muchos", "en": "many", "emoji": "🔢"},
        {"es": "pocos", "en": "few", "emoji": "🔣"},
        {"es": "ninguno", "en": "none", "emoji": "0️⃣"},
        {"es": "algunos", "en": "some", "emoji": "➕"},
    ],
    (3, 5): [
        {"es": "primero", "en": "first", "emoji": "🥇"},
        {"es": "segundo", "en": "second", "emoji": "🥈"},
        {"es": "tercero", "en": "third", "emoji": "🥉"},
        {"es": "cuarto", "en": "fourth", "emoji": "4️⃣"},
        {"es": "quinto", "en": "fifth", "emoji": "5️⃣"},
        {"es": "último", "en": "last", "emoji": "🏁"},
    ],
    (3, 6): [  # Repaso Números
        {"es": "uno", "en": "one", "emoji": "1️⃣"},
        {"es": "cinco", "en": "five", "emoji": "5️⃣"},
        {"es": "diez", "en": "ten", "emoji": "🔟"},
        {"es": "veinte", "en": "twenty", "emoji": "2️⃣0️⃣"},
        {"es": "primero", "en": "first", "emoji": "🥇"},
        {"es": "último", "en": "last", "emoji": "🏁"},
    ],
    # Sección 4 — Animales
    (4, 1): [
        {"es": "vaca", "en": "cow", "emoji": "🐄"},
        {"es": "caballo", "en": "horse", "emoji": "🐴"},
        {"es": "cerdo", "en": "pig", "emoji": "🐷"},
        {"es": "gallina", "en": "chicken", "emoji": "🐔"},
        {"es": "perro", "en": "dog", "emoji": "🐕"},
        {"es": "gato", "en": "cat", "emoji": "🐈"},
    ],
    (4, 2): [
        {"es": "león", "en": "lion", "emoji": "🦁"},
        {"es": "elefante", "en": "elephant", "emoji": "🐘"},
        {"es": "mono", "en": "monkey", "emoji": "🐒"},
        {"es": "jirafa", "en": "giraffe", "emoji": "🦒"},
        {"es": "tigre", "en": "tiger", "emoji": "🐯"},
        {"es": "serpiente", "en": "snake", "emoji": "🐍"},
    ],
    (4, 3): [
        {"es": "pez", "en": "fish", "emoji": "🐟"},
        {"es": "tiburón", "en": "shark", "emoji": "🦈"},
        {"es": "delfín", "en": "dolphin", "emoji": "🐬"},
        {"es": "pulpo", "en": "octopus", "emoji": "🐙"},
        {"es": "ballena", "en": "whale", "emoji": "🐳"},
        {"es": "cangrejo", "en": "crab", "emoji": "🦀"},
    ],
    (4, 4): [
        {"es": "ladrido", "en": "bark", "emoji": "🐕"},
        {"es": "rugido", "en": "roar", "emoji": "🦁"},
        {"es": "maullido", "en": "meow", "emoji": "🐈"},
        {"es": "mugido", "en": "moo", "emoji": "🐄"},
        {"es": "canto", "en": "chirp", "emoji": "🐦"},
        {"es": "silbido", "en": "hiss", "emoji": "🐍"},
    ],
    (4, 5): [
        {"es": "vaca", "en": "cow", "emoji": "🐄"},
        {"es": "león", "en": "lion", "emoji": "🦁"},
        {"es": "pez", "en": "fish", "emoji": "🐟"},
        {"es": "perro", "en": "dog", "emoji": "🐕"},
        {"es": "elefante", "en": "elephant", "emoji": "🐘"},
        {"es": "tiburón", "en": "shark", "emoji": "🦈"},
    ],
    # Sección 5 — Cuerpo
    (5, 1): [
        {"es": "cabeza", "en": "head", "emoji": "🗣️"},
        {"es": "ojo", "en": "eye", "emoji": "👁️"},
        {"es": "oreja", "en": "ear", "emoji": "👂"},
        {"es": "nariz", "en": "nose", "emoji": "👃"},
        {"es": "boca", "en": "mouth", "emoji": "👄"},
        {"es": "cabello", "en": "hair", "emoji": "💇"},
    ],
    (5, 2): [
        {"es": "brazo", "en": "arm", "emoji": "💪"},
        {"es": "mano", "en": "hand", "emoji": "✋"},
        {"es": "pierna", "en": "leg", "emoji": "🦵"},
        {"es": "pie", "en": "foot", "emoji": "🦶"},
        {"es": "espalda", "en": "back", "emoji": "🔙"},
        {"es": "dedo", "en": "finger", "emoji": "☝️"},
    ],
    (5, 3): [
        {"es": "feliz", "en": "happy", "emoji": "😊"},
        {"es": "triste", "en": "sad", "emoji": "😢"},
        {"es": "cansado", "en": "tired", "emoji": "😴"},
        {"es": "hambriento", "en": "hungry", "emoji": "😋"},
        {"es": "enojado", "en": "angry", "emoji": "😠"},
        {"es": "asustado", "en": "scared", "emoji": "😨"},
    ],
    (5, 4): [
        {"es": "Me duele la cabeza", "en": "My head hurts", "emoji": "🤕"},
        {"es": "Tengo fiebre", "en": "I have a fever", "emoji": "🤒"},
        {"es": "Estoy enfermo", "en": "I am sick", "emoji": "🏥"},
        {"es": "Me siento bien", "en": "I feel good", "emoji": "👍"},
        {"es": "Necesito descansar", "en": "I need to rest", "emoji": "😴"},
        {"es": "Necesito agua", "en": "I need water", "emoji": "💧"},
    ],
    (5, 5): [
        {"es": "cabeza", "en": "head", "emoji": "🗣️"},
        {"es": "mano", "en": "hand", "emoji": "✋"},
        {"es": "pie", "en": "foot", "emoji": "🦶"},
        {"es": "feliz", "en": "happy", "emoji": "😊"},
        {"es": "triste", "en": "sad", "emoji": "😢"},
        {"es": "enfermo", "en": "sick", "emoji": "🤒"},
    ],
    # Sección 6 — Comida
    (6, 1): [
        {"es": "manzana", "en": "apple", "emoji": "🍎"},
        {"es": "plátano", "en": "banana", "emoji": "🍌"},
        {"es": "zanahoria", "en": "carrot", "emoji": "🥕"},
        {"es": "tomate", "en": "tomato", "emoji": "🍅"},
        {"es": "uvas", "en": "grapes", "emoji": "🍇"},
        {"es": "lechuga", "en": "lettuce", "emoji": "🥬"},
    ],
    (6, 2): [
        {"es": "huevo", "en": "egg", "emoji": "🥚"},
        {"es": "pan", "en": "bread", "emoji": "🍞"},
        {"es": "leche", "en": "milk", "emoji": "🥛"},
        {"es": "cereal", "en": "cereal", "emoji": "🥣"},
        {"es": "mantequilla", "en": "butter", "emoji": "🧈"},
        {"es": "jugo", "en": "juice", "emoji": "🧃"},
    ],
    (6, 3): [
        {"es": "arroz", "en": "rice", "emoji": "🍚"},
        {"es": "pollo", "en": "chicken", "emoji": "🍗"},
        {"es": "sopa", "en": "soup", "emoji": "🍲"},
        {"es": "ensalada", "en": "salad", "emoji": "🥗"},
        {"es": "pasta", "en": "pasta", "emoji": "🍝"},
        {"es": "carne", "en": "meat", "emoji": "🥩"},
    ],
    (6, 4): [
        {"es": "Me gusta", "en": "I like", "emoji": "👍"},
        {"es": "No me gusta", "en": "I don't like", "emoji": "👎"},
        {"es": "Me encanta", "en": "I love", "emoji": "❤️"},
        {"es": "Odio", "en": "I hate", "emoji": "💔"},
        {"es": "Prefiero", "en": "I prefer", "emoji": "⭐"},
        {"es": "¿Te gusta?", "en": "Do you like it?", "emoji": "❓"},
    ],
    (6, 5): [
        {"es": "restaurante", "en": "restaurant", "emoji": "🍽️"},
        {"es": "menú", "en": "menu", "emoji": "📋"},
        {"es": "mesero", "en": "waiter", "emoji": "🧑‍🍳"},
        {"es": "Quiero...", "en": "I would like...", "emoji": "🤲"},
        {"es": "La cuenta", "en": "The check", "emoji": "💳"},
        {"es": "Delicioso", "en": "Delicious", "emoji": "😋"},
    ],
    (6, 6): [
        {"es": "manzana", "en": "apple", "emoji": "🍎"},
        {"es": "huevo", "en": "egg", "emoji": "🥚"},
        {"es": "arroz", "en": "rice", "emoji": "🍚"},
        {"es": "Me gusta", "en": "I like", "emoji": "👍"},
        {"es": "restaurante", "en": "restaurant", "emoji": "🍽️"},
        {"es": "delicioso", "en": "delicious", "emoji": "😋"},
    ],
    # Sección 7 — Casa
    (7, 1): [
        {"es": "sala", "en": "living room", "emoji": "🛋️"},
        {"es": "cocina", "en": "kitchen", "emoji": "🍳"},
        {"es": "cuarto", "en": "bedroom", "emoji": "🛏️"},
        {"es": "baño", "en": "bathroom", "emoji": "🚿"},
        {"es": "jardín", "en": "garden", "emoji": "🌻"},
        {"es": "garaje", "en": "garage", "emoji": "🚗"},
    ],
    (7, 2): [
        {"es": "mesa", "en": "table", "emoji": "🪑"},
        {"es": "silla", "en": "chair", "emoji": "🪑"},
        {"es": "cama", "en": "bed", "emoji": "🛏️"},
        {"es": "lámpara", "en": "lamp", "emoji": "💡"},
        {"es": "televisor", "en": "television", "emoji": "📺"},
        {"es": "nevera", "en": "refrigerator", "emoji": "🧊"},
    ],
    (7, 3): [
        {"es": "adentro", "en": "inside", "emoji": "🏠"},
        {"es": "afuera", "en": "outside", "emoji": "🌳"},
        {"es": "encima", "en": "on top of", "emoji": "⬆️"},
        {"es": "debajo", "en": "under", "emoji": "⬇️"},
        {"es": "al lado", "en": "next to", "emoji": "↔️"},
        {"es": "detrás", "en": "behind", "emoji": "↩️"},
    ],
    (7, 4): [
        {"es": "mi habitación", "en": "my bedroom", "emoji": "🛏️"},
        {"es": "Mi cama es...", "en": "My bed is...", "emoji": "🛏️"},
        {"es": "Tengo una ventana", "en": "I have a window", "emoji": "🪟"},
        {"es": "Mi cuarto es grande", "en": "My room is big", "emoji": "📐"},
        {"es": "El piso es de madera", "en": "The floor is wood", "emoji": "🪵"},
        {"es": "Hay muchos juguetes", "en": "There are many toys", "emoji": "🧸"},
    ],
    (7, 5): [
        {"es": "sala", "en": "living room", "emoji": "🛋️"},
        {"es": "cocina", "en": "kitchen", "emoji": "🍳"},
        {"es": "cama", "en": "bed", "emoji": "🛏️"},
        {"es": "encima", "en": "on top of", "emoji": "⬆️"},
        {"es": "debajo", "en": "under", "emoji": "⬇️"},
        {"es": "al lado", "en": "next to", "emoji": "↔️"},
    ],
    # Sección 8 — Tiempo
    (8, 1): [
        {"es": "soleado", "en": "sunny", "emoji": "☀️"},
        {"es": "nublado", "en": "cloudy", "emoji": "☁️"},
        {"es": "lluvioso", "en": "rainy", "emoji": "🌧️"},
        {"es": "ventoso", "en": "windy", "emoji": "💨"},
        {"es": "nevado", "en": "snowy", "emoji": "❄️"},
        {"es": "caliente", "en": "hot", "emoji": "🥵"},
    ],
    (8, 2): [
        {"es": "primavera", "en": "spring", "emoji": "🌸"},
        {"es": "verano", "en": "summer", "emoji": "☀️"},
        {"es": "otoño", "en": "fall/autumn", "emoji": "🍂"},
        {"es": "invierno", "en": "winter", "emoji": "❄️"},
        {"es": "estación", "en": "season", "emoji": "🌍"},
        {"es": "año", "en": "year", "emoji": "📅"},
    ],
    (8, 3): [
        {"es": "abrigo", "en": "coat", "emoji": "🧥"},
        {"es": "botas", "en": "boots", "emoji": "👢"},
        {"es": "sombrilla", "en": "umbrella", "emoji": "☂️"},
        {"es": "gafas de sol", "en": "sunglasses", "emoji": "😎"},
        {"es": "suéter", "en": "sweater", "emoji": "🧶"},
        {"es": "sandalias", "en": "sandals", "emoji": "👡"},
    ],
    (8, 4): [
        {"es": "enero", "en": "January", "emoji": "1️⃣"},
        {"es": "febrero", "en": "February", "emoji": "2️⃣"},
        {"es": "marzo", "en": "March", "emoji": "3️⃣"},
        {"es": "junio", "en": "June", "emoji": "6️⃣"},
        {"es": "diciembre", "en": "December", "emoji": "1️⃣2️⃣"},
        {"es": "mes", "en": "month", "emoji": "📅"},
    ],
    (8, 5): [
        {"es": "soleado", "en": "sunny", "emoji": "☀️"},
        {"es": "lluvioso", "en": "rainy", "emoji": "🌧️"},
        {"es": "primavera", "en": "spring", "emoji": "🌸"},
        {"es": "invierno", "en": "winter", "emoji": "❄️"},
        {"es": "abrigo", "en": "coat", "emoji": "🧥"},
        {"es": "enero", "en": "January", "emoji": "1️⃣"},
    ],
    # Sección 9 — Actividades
    (9, 1): [
        {"es": "fútbol", "en": "soccer", "emoji": "⚽"},
        {"es": "baloncesto", "en": "basketball", "emoji": "🏀"},
        {"es": "natación", "en": "swimming", "emoji": "🏊"},
        {"es": "béisbol", "en": "baseball", "emoji": "⚾"},
        {"es": "ciclismo", "en": "cycling", "emoji": "🚴"},
        {"es": "atletismo", "en": "track and field", "emoji": "🏃"},
    ],
    (9, 2): [
        {"es": "leer", "en": "reading", "emoji": "📚"},
        {"es": "dibujar", "en": "drawing", "emoji": "✏️"},
        {"es": "bailar", "en": "dancing", "emoji": "💃"},
        {"es": "cantar", "en": "singing", "emoji": "🎤"},
        {"es": "cocinar", "en": "cooking", "emoji": "🍳"},
        {"es": "videojuegos", "en": "video games", "emoji": "🎮"},
    ],
    (9, 3): [
        {"es": "lunes", "en": "Monday", "emoji": "1️⃣"},
        {"es": "martes", "en": "Tuesday", "emoji": "2️⃣"},
        {"es": "miércoles", "en": "Wednesday", "emoji": "3️⃣"},
        {"es": "jueves", "en": "Thursday", "emoji": "4️⃣"},
        {"es": "viernes", "en": "Friday", "emoji": "5️⃣"},
        {"es": "fin de semana", "en": "weekend", "emoji": "🎉"},
    ],
    (9, 4): [
        {"es": "después del colegio", "en": "after school", "emoji": "🏫"},
        {"es": "Voy a...", "en": "I go to...", "emoji": "🚶"},
        {"es": "Juego...", "en": "I play...", "emoji": "🎮"},
        {"es": "Hago mis tareas", "en": "I do my homework", "emoji": "📝"},
        {"es": "Como con mi familia", "en": "I eat with my family", "emoji": "🍽️"},
        {"es": "Me duermo a las...", "en": "I go to sleep at...", "emoji": "😴"},
    ],
    (9, 5): [
        {"es": "fútbol", "en": "soccer", "emoji": "⚽"},
        {"es": "dibujar", "en": "drawing", "emoji": "✏️"},
        {"es": "lunes", "en": "Monday", "emoji": "1️⃣"},
        {"es": "viernes", "en": "Friday", "emoji": "5️⃣"},
        {"es": "Juego...", "en": "I play...", "emoji": "🎮"},
        {"es": "Hago mis tareas", "en": "I do my homework", "emoji": "📝"},
    ],
    # Sección 10 — Comunidad
    (10, 1): [
        {"es": "colegio", "en": "school", "emoji": "🏫"},
        {"es": "parque", "en": "park", "emoji": "🌳"},
        {"es": "mercado", "en": "market", "emoji": "🛒"},
        {"es": "hospital", "en": "hospital", "emoji": "🏥"},
        {"es": "iglesia", "en": "church", "emoji": "⛪"},
        {"es": "biblioteca", "en": "library", "emoji": "📚"},
    ],
    (10, 2): [
        {"es": "gira a la izquierda", "en": "turn left", "emoji": "⬅️"},
        {"es": "gira a la derecha", "en": "turn right", "emoji": "➡️"},
        {"es": "sigue derecho", "en": "go straight", "emoji": "⬆️"},
        {"es": "para", "en": "stop", "emoji": "🛑"},
        {"es": "cerca", "en": "near", "emoji": "📍"},
        {"es": "lejos", "en": "far", "emoji": "🗺️"},
    ],
    (10, 3): [
        {"es": "bus", "en": "bus", "emoji": "🚌"},
        {"es": "carro", "en": "car", "emoji": "🚗"},
        {"es": "bicicleta", "en": "bicycle", "emoji": "🚲"},
        {"es": "moto", "en": "motorcycle", "emoji": "🏍️"},
        {"es": "taxi", "en": "taxi", "emoji": "🚕"},
        {"es": "a pie", "en": "on foot", "emoji": "🚶"},
    ],
    (10, 4): [
        {"es": "vecino", "en": "neighbor", "emoji": "👋"},
        {"es": "comunidad", "en": "community", "emoji": "🏘️"},
        {"es": "calle", "en": "street", "emoji": "🛣️"},
        {"es": "barrio", "en": "neighborhood", "emoji": "🏙️"},
        {"es": "pueblo", "en": "town", "emoji": "🏡"},
        {"es": "ciudad", "en": "city", "emoji": "🌆"},
    ],
    (10, 5): [
        {"es": "colegio", "en": "school", "emoji": "🏫"},
        {"es": "bus", "en": "bus", "emoji": "🚌"},
        {"es": "gira a la izquierda", "en": "turn left", "emoji": "⬅️"},
        {"es": "sigue derecho", "en": "go straight", "emoji": "⬆️"},
        {"es": "comunidad", "en": "community", "emoji": "🏘️"},
        {"es": "ciudad", "en": "city", "emoji": "🌆"},
    ],
}


# ── Minijuego rotation & difficulty ──────────────────────────────────────────

TIPO_ROTATION = ['memoria', 'verdadero_falso', 'rellenar', 'clasificar', 'ordenar_oracion', 'unir_pares']

TITULOS_MINIJUEGO = {
    'memoria':         '¡Memoria!',
    'verdadero_falso': '¿Verdadero o Falso?',
    'rellenar':        '¡Rellena el espacio!',
    'clasificar':      '¡Clasifica las palabras!',
    'ordenar_oracion': '¡Arma la oración!',
    'unir_pares':      '¡Une los pares!',
}

INSTRUCCIONES_MINIJUEGO = {
    'memoria':         'Voltea las tarjetas y encuentra los pares que coinciden.',
    'verdadero_falso': 'Lee cada frase y elige si es verdadera o falsa.',
    'rellenar':        'Escribe la palabra que falta en cada oración.',
    'clasificar':      'Arrastra cada palabra al grupo donde pertenece.',
    'ordenar_oracion': 'Toca las palabras en el orden correcto para formar la oración.',
    'unir_pares':      'Toca una palabra de la izquierda y luego su pareja de la derecha.',
}

def get_dificultad(seccion_orden):
    """Returns difficulty level 1-4 based on section (chapter) order."""
    if seccion_orden <= 2: return 1
    if seccion_orden <= 5: return 2
    if seccion_orden <= 8: return 3
    return 4

# Max items per difficulty level per tipo
DIFFICULTY_PARAMS = {
    'memoria':         {1: 4, 2: 4, 3: 5, 4: 6},
    'unir_pares':      {1: 3, 2: 4, 3: 5, 4: 6},
    'verdadero_falso': {1: 2, 2: 3, 3: 3, 4: 4},
    'rellenar':        {1: 1, 2: 2, 3: 2, 4: 3},
    'ordenar_oracion': {1: 1, 2: 1, 3: 2, 4: 3},
}

# ── Manual content per section ────────────────────────────────────────────────
# Keys: seccion_pk (1-10). Each has lists of variant dicts for the 4 manually-
# crafted types. memoria and unir_pares are auto-generated from VOCABULARIO.
# Each list should have 4 variants so difficulty slicing always leaves 3+ good ones.

MINIJUEGO_CONTENT = {
    1: {  # Los Colores del Mundo — D1
        'ordenar_oracion': [
            {'oraciones': ['The sky is blue']},
            {'oraciones': ['Red is my favorite color']},
            {'oraciones': ['I like yellow and green']},
            {'oraciones': ['The sun is bright yellow']},
        ],
        'rellenar': [
            {'oraciones': [{'texto': 'The ___ is red.', 'respuesta': 'apple', 'emoji': '🍎'}]},
            {'oraciones': [{'texto': 'The sky is ___.', 'respuesta': 'blue', 'emoji': '🌤️'}]},
            {'oraciones': [{'texto': 'Grass is ___.', 'respuesta': 'green', 'emoji': '🌿'}]},
            {'oraciones': [{'texto': 'The sun is ___.', 'respuesta': 'yellow', 'emoji': '☀️'}]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'Red is a primary color.', 'respuesta': True, 'explicacion': 'Yes! Red, blue, and yellow are the three primary colors.'},
                {'afirmacion': 'The sky is green.', 'respuesta': False, 'explicacion': 'The sky is blue, not green!'},
                {'afirmacion': 'Orange is made by mixing red and yellow.', 'respuesta': True, 'explicacion': 'Correct! Orange is a secondary color made from red + yellow.'},
                {'afirmacion': 'Black is a light color.', 'respuesta': False, 'explicacion': 'Black is the darkest color. White is the lightest.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Yellow is a warm color.', 'respuesta': True, 'explicacion': 'Yes! Red, orange, and yellow are warm colors.'},
                {'afirmacion': 'Blue is a secondary color.', 'respuesta': False, 'explicacion': 'Blue is a primary color — it cannot be made by mixing others.'},
                {'afirmacion': 'Pink is a mix of red and white.', 'respuesta': True, 'explicacion': 'Correct! Pink is made by adding white to red.'},
                {'afirmacion': 'Green is a primary color.', 'respuesta': False, 'explicacion': 'Green is secondary — it is made by mixing blue and yellow.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'White is a light color.', 'respuesta': True, 'explicacion': 'Yes! White is the lightest color of all.'},
                {'afirmacion': 'Purple is made from blue and red.', 'respuesta': True, 'explicacion': 'Correct! Purple is a secondary color made from blue + red.'},
                {'afirmacion': 'A banana is red.', 'respuesta': False, 'explicacion': 'A banana is yellow, not red!'},
                {'afirmacion': 'Gray is a mix of black and white.', 'respuesta': True, 'explicacion': 'Yes! Gray is made by mixing black and white together.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Colores primarios', 'emoji': '🎨', 'items': ['red', 'blue', 'yellow']},
                {'nombre': 'Colores secundarios', 'emoji': '🖌️', 'items': ['green', 'orange', 'purple']},
            ]},
            {'categorias': [
                {'nombre': 'Colores cálidos', 'emoji': '☀️', 'items': ['red', 'orange', 'yellow']},
                {'nombre': 'Colores fríos', 'emoji': '❄️', 'items': ['blue', 'green', 'purple']},
            ]},
            {'categorias': [
                {'nombre': 'Colores oscuros', 'emoji': '🌑', 'items': ['black', 'dark blue', 'dark green']},
                {'nombre': 'Colores claros', 'emoji': '🌟', 'items': ['white', 'pink', 'light blue']},
            ]},
        ],
    },
    2: {  # Mi Familia y Yo — D1
        'ordenar_oracion': [
            {'oraciones': ['She is my mother']},
            {'oraciones': ['He is my brother']},
            {'oraciones': ['I love my family']},
            {'oraciones': ['My sister is very tall']},
        ],
        'rellenar': [
            {'oraciones': [{'texto': 'My ___ is tall.', 'respuesta': 'father', 'emoji': '👨'}]},
            {'oraciones': [{'texto': 'I have a ___.', 'respuesta': 'sister', 'emoji': '👧'}]},
            {'oraciones': [{'texto': 'My ___ is kind.', 'respuesta': 'mother', 'emoji': '👩'}]},
            {'oraciones': [{'texto': 'He is my ___.', 'respuesta': 'brother', 'emoji': '👦'}]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'A mother is a woman.', 'respuesta': True, 'explicacion': 'Yes! Mother means mamá in English.'},
                {'afirmacion': 'A brother is a girl.', 'respuesta': False, 'explicacion': 'A brother is a boy. A girl is called a sister.'},
                {'afirmacion': 'Parents are mother and father.', 'respuesta': True, 'explicacion': 'Correct! Parents means mamá y papá in English.'},
                {'afirmacion': 'Grandparents are younger than parents.', 'respuesta': False, 'explicacion': 'Grandparents are older — they are the parents of your parents.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A sister is a girl.', 'respuesta': True, 'explicacion': 'Yes! A sister is a girl who shares the same parents as you.'},
                {'afirmacion': 'An uncle is a child.', 'respuesta': False, 'explicacion': 'An uncle is an adult — the brother of your mother or father.'},
                {'afirmacion': 'Twins are born on the same day.', 'respuesta': True, 'explicacion': 'Yes! Twins are two siblings born at the same time.'},
                {'afirmacion': 'A grandmother is a young person.', 'respuesta': False, 'explicacion': 'A grandmother is older — she is the mother of your parents.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A father is a man.', 'respuesta': True, 'explicacion': 'Correct! Father means papá — he is a man.'},
                {'afirmacion': 'A cousin is your brother or sister.', 'respuesta': False, 'explicacion': 'A cousin is the child of your aunt or uncle.'},
                {'afirmacion': 'A family can be big or small.', 'respuesta': True, 'explicacion': 'Yes! Some families are big, others are small.'},
                {'afirmacion': 'A niece is a boy.', 'respuesta': False, 'explicacion': 'A niece is a girl. A boy is called a nephew.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Familia directa', 'emoji': '🏠', 'items': ['father', 'mother', 'brother', 'sister']},
                {'nombre': 'Familia extendida', 'emoji': '👨‍👩‍👧‍👦', 'items': ['grandfather', 'grandmother', 'uncle', 'aunt']},
            ]},
            {'categorias': [
                {'nombre': 'Hombres', 'emoji': '👨', 'items': ['father', 'brother', 'grandfather', 'uncle']},
                {'nombre': 'Mujeres', 'emoji': '👩', 'items': ['mother', 'sister', 'grandmother', 'aunt']},
            ]},
            {'categorias': [
                {'nombre': 'Mayores', 'emoji': '👴', 'items': ['grandfather', 'grandmother', 'father', 'mother']},
                {'nombre': 'Jóvenes', 'emoji': '👦', 'items': ['brother', 'sister', 'cousin']},
            ]},
        ],
    },
    3: {  # Los Números Mágicos — D2
        'ordenar_oracion': [
            {'oraciones': ['I have two brothers']},
            {'oraciones': ['There are five cats']},
            {'oraciones': ['She is ten years old']},
            {'oraciones': ['My sister has three dogs']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I am ___ years old.', 'respuesta': 'ten', 'emoji': '🔟'},
                {'texto': 'There are ___ dogs.', 'respuesta': 'five', 'emoji': '🐕'},
            ]},
            {'oraciones': [
                {'texto': 'He has ___ apples.', 'respuesta': 'three', 'emoji': '🍎'},
                {'texto': 'I see ___ birds.', 'respuesta': 'four', 'emoji': '🐦'},
            ]},
            {'oraciones': [
                {'texto': 'There are ___ months in a year.', 'respuesta': 'twelve', 'emoji': '📅'},
                {'texto': 'A week has ___ days.', 'respuesta': 'seven', 'emoji': '📆'},
            ]},
            {'oraciones': [
                {'texto': 'I have ___ fingers on each hand.', 'respuesta': 'five', 'emoji': '✋'},
                {'texto': 'I count to ___.', 'respuesta': 'twenty', 'emoji': '2️⃣0️⃣'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'Ten is more than five.', 'respuesta': True, 'explicacion': 'Yes! Ten (10) is bigger than five (5).'},
                {'afirmacion': 'Twenty comes before ten.', 'respuesta': False, 'explicacion': 'Ten (10) comes before twenty (20). 10 < 20.'},
                {'afirmacion': 'First is number one.', 'respuesta': True, 'explicacion': 'Correct! First is the ordinal form of the number one.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Fifteen is between ten and twenty.', 'respuesta': True, 'explicacion': 'Yes! 10 < 15 < 20.'},
                {'afirmacion': 'Two plus two equals five.', 'respuesta': False, 'explicacion': 'Two plus two equals four (2 + 2 = 4).'},
                {'afirmacion': 'Third comes after second.', 'respuesta': True, 'explicacion': 'Correct! The order is: first, second, third...'},
            ]},
            {'preguntas': [
                {'afirmacion': 'One hundred is more than fifty.', 'respuesta': True, 'explicacion': 'Yes! 100 is bigger than 50.'},
                {'afirmacion': 'Fourth is before third.', 'respuesta': False, 'explicacion': 'Third comes before fourth: first, second, third, fourth.'},
                {'afirmacion': 'Twenty is less than thirty.', 'respuesta': True, 'explicacion': 'Yes! 20 < 30.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Del 1 al 5', 'emoji': '🖐️', 'items': ['one', 'two', 'three', 'four', 'five']},
                {'nombre': 'Del 6 al 10', 'emoji': '🔟', 'items': ['six', 'seven', 'eight', 'nine', 'ten']},
            ]},
            {'categorias': [
                {'nombre': 'Números pares', 'emoji': '2️⃣', 'items': ['two', 'four', 'six', 'eight', 'ten']},
                {'nombre': 'Números impares', 'emoji': '1️⃣', 'items': ['one', 'three', 'five', 'seven', 'nine']},
            ]},
            {'categorias': [
                {'nombre': 'Ordinales', 'emoji': '🥇', 'items': ['first', 'second', 'third']},
                {'nombre': 'Cardinales', 'emoji': '🔢', 'items': ['one', 'two', 'three', 'four', 'five', 'ten']},
            ]},
        ],
    },
    4: {  # Animales del Mundo — D2
        'ordenar_oracion': [
            {'oraciones': ['The dog is very big']},
            {'oraciones': ['I like the little cat']},
            {'oraciones': ['The lion is very fast']},
            {'oraciones': ['The fish lives in water']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'The ___ says meow.', 'respuesta': 'cat', 'emoji': '🐱'},
                {'texto': 'A ___ lives on a farm.', 'respuesta': 'cow', 'emoji': '🐄'},
            ]},
            {'oraciones': [
                {'texto': 'The ___ is the king of the jungle.', 'respuesta': 'lion', 'emoji': '🦁'},
                {'texto': 'A ___ can swim very fast.', 'respuesta': 'fish', 'emoji': '🐟'},
            ]},
            {'oraciones': [
                {'texto': 'The ___ has a very long neck.', 'respuesta': 'giraffe', 'emoji': '🦒'},
                {'texto': 'A ___ is a very big sea animal.', 'respuesta': 'whale', 'emoji': '🐳'},
            ]},
            {'oraciones': [
                {'texto': 'The ___ says bark.', 'respuesta': 'dog', 'emoji': '🐕'},
                {'texto': 'An ___ is very big and gray.', 'respuesta': 'elephant', 'emoji': '🐘'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'A dog is a pet.', 'respuesta': True, 'explicacion': 'Yes! Dogs are very common pets that live with families.'},
                {'afirmacion': 'A lion lives on a farm.', 'respuesta': False, 'explicacion': 'Lions live in the savanna, not on a farm!'},
                {'afirmacion': 'Fish live in water.', 'respuesta': True, 'explicacion': 'Yes! Fish live in rivers, lakes, and the ocean.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A cat says bark.', 'respuesta': False, 'explicacion': 'A cat says meow! Dogs say bark.'},
                {'afirmacion': 'Elephants are big animals.', 'respuesta': True, 'explicacion': 'Yes! Elephants are the largest land animals.'},
                {'afirmacion': 'A shark lives in the forest.', 'respuesta': False, 'explicacion': 'Sharks live in the ocean, not in the forest!'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A cow gives us milk.', 'respuesta': True, 'explicacion': 'Yes! Cows are farm animals that produce milk.'},
                {'afirmacion': 'A monkey can fly.', 'respuesta': False, 'explicacion': 'Monkeys cannot fly — they swing from tree to tree!'},
                {'afirmacion': 'A dolphin is a smart animal.', 'respuesta': True, 'explicacion': 'Yes! Dolphins are very intelligent sea animals.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Animales de granja', 'emoji': '🌾', 'items': ['cow', 'pig', 'chicken', 'horse', 'dog', 'cat']},
                {'nombre': 'Animales salvajes', 'emoji': '🌿', 'items': ['lion', 'elephant', 'monkey', 'giraffe', 'tiger', 'snake']},
            ]},
            {'categorias': [
                {'nombre': 'Animales del mar', 'emoji': '🌊', 'items': ['fish', 'shark', 'dolphin', 'whale', 'octopus', 'crab']},
                {'nombre': 'Animales de tierra', 'emoji': '🌍', 'items': ['dog', 'cat', 'cow', 'horse', 'lion', 'elephant']},
            ]},
            {'categorias': [
                {'nombre': 'Animales grandes', 'emoji': '🐘', 'items': ['elephant', 'whale', 'horse', 'cow', 'lion', 'giraffe']},
                {'nombre': 'Animales pequeños', 'emoji': '🐱', 'items': ['cat', 'fish', 'crab', 'snake', 'chicken', 'monkey']},
            ]},
        ],
    },
    5: {  # Mi Cuerpo — D2
        'ordenar_oracion': [
            {'oraciones': ['My head is on top']},
            {'oraciones': ['I wash my hands every day']},
            {'oraciones': ['My feet are on the floor']},
            {'oraciones': ['She has beautiful blue eyes']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I have two ___.', 'respuesta': 'hands', 'emoji': '✋'},
                {'texto': 'My ___ are on my face.', 'respuesta': 'eyes', 'emoji': '👁️'},
            ]},
            {'oraciones': [
                {'texto': 'My ___ hurts today.', 'respuesta': 'head', 'emoji': '🗣️'},
                {'texto': 'I use my ___ to walk.', 'respuesta': 'feet', 'emoji': '🦶'},
            ]},
            {'oraciones': [
                {'texto': 'She is ___ today.', 'respuesta': 'happy', 'emoji': '😊'},
                {'texto': 'He feels very ___.', 'respuesta': 'tired', 'emoji': '😴'},
            ]},
            {'oraciones': [
                {'texto': 'I use my ___ to hear.', 'respuesta': 'ears', 'emoji': '👂'},
                {'texto': 'My ___ is very strong.', 'respuesta': 'arm', 'emoji': '💪'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'We have two eyes.', 'respuesta': True, 'explicacion': 'Yes! Most people have two eyes on their face.'},
                {'afirmacion': 'A nose is on the arm.', 'respuesta': False, 'explicacion': 'A nose is on the face, not on the arm!'},
                {'afirmacion': 'Feet are at the bottom of the body.', 'respuesta': True, 'explicacion': 'Yes! Feet are at the very bottom of our body.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'We use our ears to see.', 'respuesta': False, 'explicacion': 'We use our ears to hear. We use our eyes to see!'},
                {'afirmacion': 'A hand has five fingers.', 'respuesta': True, 'explicacion': 'Yes! Each hand has five fingers.'},
                {'afirmacion': 'Happy and sad are feelings.', 'respuesta': True, 'explicacion': 'Correct! Happy and sad describe how we feel.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'We breathe with our nose.', 'respuesta': True, 'explicacion': 'Yes! We breathe in and out through our nose.'},
                {'afirmacion': 'Legs are on our head.', 'respuesta': False, 'explicacion': 'Legs are at the bottom of our body!'},
                {'afirmacion': 'Being hungry is a feeling.', 'respuesta': True, 'explicacion': 'Yes! Hungry, tired, happy — these are all feelings.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Partes de la cara', 'emoji': '😊', 'items': ['eye', 'nose', 'mouth', 'ear', 'hair']},
                {'nombre': 'Partes del cuerpo', 'emoji': '💪', 'items': ['arm', 'hand', 'leg', 'foot', 'back']},
            ]},
            {'categorias': [
                {'nombre': 'Sentimientos positivos', 'emoji': '😊', 'items': ['happy', 'excited', 'proud']},
                {'nombre': 'Sentimientos negativos', 'emoji': '😢', 'items': ['sad', 'angry', 'scared', 'tired', 'hungry']},
            ]},
            {'categorias': [
                {'nombre': 'Arriba del cuerpo', 'emoji': '🗣️', 'items': ['head', 'eye', 'ear', 'nose', 'mouth', 'arm']},
                {'nombre': 'Abajo del cuerpo', 'emoji': '🦵', 'items': ['leg', 'foot', 'knee', 'toe']},
            ]},
        ],
    },
    6: {  # La Comida Rica — D3
        'ordenar_oracion': [
            {'oraciones': ['I like apples and bananas', 'Carrots are orange vegetables']},
            {'oraciones': ['She eats eggs for breakfast', 'Milk is good for you']},
            {'oraciones': ['I would like some rice please', 'The salad is fresh and green']},
            {'oraciones': ['Do you like this food', 'I love eating with my family']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'An ___ a day keeps the doctor away.', 'respuesta': 'apple', 'emoji': '🍎'},
                {'texto': 'I drink ___ every morning.', 'respuesta': 'milk', 'emoji': '🥛'},
            ]},
            {'oraciones': [
                {'texto': 'I like ___ with butter.', 'respuesta': 'bread', 'emoji': '🍞'},
                {'texto': 'Fried ___ is a great breakfast.', 'respuesta': 'egg', 'emoji': '🥚'},
            ]},
            {'oraciones': [
                {'texto': 'My mom cooks ___ with chicken.', 'respuesta': 'rice', 'emoji': '🍚'},
                {'texto': 'I love tomato ___.', 'respuesta': 'soup', 'emoji': '🍲'},
            ]},
            {'oraciones': [
                {'texto': 'I ___ pizza very much.', 'respuesta': 'like', 'emoji': '🍕'},
                {'texto': 'The food is ___.', 'respuesta': 'delicious', 'emoji': '😋'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'An apple is a fruit.', 'respuesta': True, 'explicacion': 'Yes! Apples, bananas, and grapes are all fruits.'},
                {'afirmacion': 'A carrot is a fruit.', 'respuesta': False, 'explicacion': 'A carrot is a vegetable, not a fruit!'},
                {'afirmacion': 'Milk comes from cows.', 'respuesta': True, 'explicacion': 'Yes! Cows give us milk.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Bread is a breakfast food.', 'respuesta': True, 'explicacion': 'Yes! Bread with butter or jam is a common breakfast.'},
                {'afirmacion': 'Rice is a vegetable.', 'respuesta': False, 'explicacion': 'Rice is a grain or cereal, not a vegetable.'},
                {'afirmacion': '"I like" means "me gusta" in English.', 'respuesta': True, 'explicacion': 'Correct! "I like pizza" = "Me gusta la pizza."'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Breakfast is the first meal of the day.', 'respuesta': True, 'explicacion': 'Yes! Breakfast is the meal we eat in the morning.'},
                {'afirmacion': 'A banana is a vegetable.', 'respuesta': False, 'explicacion': 'A banana is a fruit, not a vegetable!'},
                {'afirmacion': 'Delicious means very tasty.', 'respuesta': True, 'explicacion': 'Yes! Delicious means that food tastes very good.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Frutas', 'emoji': '🍎', 'items': ['apple', 'banana', 'grapes', 'mango', 'orange']},
                {'nombre': 'Verduras', 'emoji': '🥕', 'items': ['carrot', 'lettuce', 'tomato', 'potato', 'onion']},
            ]},
            {'categorias': [
                {'nombre': 'Desayuno', 'emoji': '🌅', 'items': ['egg', 'bread', 'milk', 'cereal', 'juice', 'butter']},
                {'nombre': 'Almuerzo / Cena', 'emoji': '🍽️', 'items': ['rice', 'chicken', 'soup', 'salad', 'pasta', 'meat']},
            ]},
            {'categorias': [
                {'nombre': 'Me gusta ❤️', 'emoji': '👍', 'items': ['pizza', 'apple', 'rice', 'milk']},
                {'nombre': 'No me gusta 💔', 'emoji': '👎', 'items': ['broccoli', 'liver', 'raw onion', 'bitter melon']},
            ]},
        ],
    },
    7: {  # Mi Casa y mis Cosas — D3
        'ordenar_oracion': [
            {'oraciones': ['My bedroom is very big', 'I sleep in my bed every night']},
            {'oraciones': ['The kitchen has a refrigerator', 'We eat in the dining room']},
            {'oraciones': ['The book is on the table', 'My shoes are under the bed']},
            {'oraciones': ['I watch TV in the living room', 'My room has a big window']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I sleep in my ___.', 'respuesta': 'bed', 'emoji': '🛏️'},
                {'texto': 'We cook in the ___.', 'respuesta': 'kitchen', 'emoji': '🍳'},
            ]},
            {'oraciones': [
                {'texto': 'The cat is ___ the table.', 'respuesta': 'under', 'emoji': '⬇️'},
                {'texto': 'My book is ___ the desk.', 'respuesta': 'on', 'emoji': '📚'},
            ]},
            {'oraciones': [
                {'texto': 'I watch TV in the ___ room.', 'respuesta': 'living', 'emoji': '📺'},
                {'texto': 'The ___ keeps food cold.', 'respuesta': 'refrigerator', 'emoji': '🧊'},
            ]},
            {'oraciones': [
                {'texto': 'My room is ___ the bathroom.', 'respuesta': 'next to', 'emoji': '↔️'},
                {'texto': 'The lamp is ___ the table.', 'respuesta': 'on', 'emoji': '💡'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'A bedroom is where you sleep.', 'respuesta': True, 'explicacion': 'Yes! We sleep in the bedroom.'},
                {'afirmacion': 'We cook food in the bathroom.', 'respuesta': False, 'explicacion': 'We cook food in the kitchen, not the bathroom!'},
                {'afirmacion': '"Under" means debajo.', 'respuesta': True, 'explicacion': 'Correct! Under means debajo in Spanish.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A refrigerator keeps food cold.', 'respuesta': True, 'explicacion': 'Yes! The refrigerator keeps food fresh and cold.'},
                {'afirmacion': '"Next to" means debajo.', 'respuesta': False, 'explicacion': '"Next to" means al lado. "Under" means debajo.'},
                {'afirmacion': 'A living room has a sofa.', 'respuesta': True, 'explicacion': 'Yes! We usually have a sofa and TV in the living room.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A lamp gives light.', 'respuesta': True, 'explicacion': 'Yes! We turn on a lamp to light up a room.'},
                {'afirmacion': '"On top of" means debajo.', 'respuesta': False, 'explicacion': '"On top of" means encima. "Under" means debajo.'},
                {'afirmacion': 'A table is a piece of furniture.', 'respuesta': True, 'explicacion': 'Yes! Tables, chairs, and beds are all furniture.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Cuartos', 'emoji': '🏠', 'items': ['living room', 'kitchen', 'bedroom', 'bathroom', 'garage', 'garden']},
                {'nombre': 'Muebles', 'emoji': '🛋️', 'items': ['table', 'chair', 'bed', 'lamp', 'sofa', 'desk']},
            ]},
            {'categorias': [
                {'nombre': 'Encima / Sobre', 'emoji': '⬆️', 'items': ['on', 'on top of', 'above']},
                {'nombre': 'Abajo / Al lado', 'emoji': '⬇️', 'items': ['under', 'below', 'next to', 'behind']},
            ]},
            {'categorias': [
                {'nombre': 'En la cocina', 'emoji': '🍳', 'items': ['refrigerator', 'stove', 'table', 'fork', 'plate']},
                {'nombre': 'En la habitación', 'emoji': '🛏️', 'items': ['bed', 'pillow', 'lamp', 'desk', 'closet']},
            ]},
        ],
    },
    8: {  # El Tiempo y las Estaciones — D3
        'ordenar_oracion': [
            {'oraciones': ['Today the weather is sunny', 'I wear a coat when it is cold']},
            {'oraciones': ['Spring is my favorite season', 'Flowers bloom in spring']},
            {'oraciones': ['In winter we wear boots', 'Snow falls in December']},
            {'oraciones': ['Summer is hot and sunny', 'We swim in the summer']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'Today is ___ and warm.', 'respuesta': 'sunny', 'emoji': '☀️'},
                {'texto': 'I use my ___ when it rains.', 'respuesta': 'umbrella', 'emoji': '☂️'},
            ]},
            {'oraciones': [
                {'texto': 'In ___, flowers bloom.', 'respuesta': 'spring', 'emoji': '🌸'},
                {'texto': 'I wear a ___ in winter.', 'respuesta': 'coat', 'emoji': '🧥'},
            ]},
            {'oraciones': [
                {'texto': 'It is very ___ in summer.', 'respuesta': 'hot', 'emoji': '🥵'},
                {'texto': 'December is a ___ month.', 'respuesta': 'winter', 'emoji': '❄️'},
            ]},
            {'oraciones': [
                {'texto': 'It is ___ today, bring an umbrella.', 'respuesta': 'rainy', 'emoji': '🌧️'},
                {'texto': 'The wind is very ___ today.', 'respuesta': 'strong', 'emoji': '💨'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'Summer is the hottest season.', 'respuesta': True, 'explicacion': 'Yes! Summer is the warmest time of the year.'},
                {'afirmacion': 'It snows in summer.', 'respuesta': False, 'explicacion': 'It usually snows in winter, not in summer!'},
                {'afirmacion': 'We use an umbrella when it rains.', 'respuesta': True, 'explicacion': 'Yes! An umbrella protects us from the rain.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Spring comes after winter.', 'respuesta': True, 'explicacion': 'Yes! Winter → Spring → Summer → Fall.'},
                {'afirmacion': 'A coat is used in summer.', 'respuesta': False, 'explicacion': 'We wear coats in cold weather, not in summer!'},
                {'afirmacion': 'There are four seasons in a year.', 'respuesta': True, 'explicacion': 'Yes! Spring, summer, fall, and winter.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'December is a winter month.', 'respuesta': True, 'explicacion': 'Yes! December is in winter in the Northern Hemisphere.'},
                {'afirmacion': 'Windy means very cold.', 'respuesta': False, 'explicacion': 'Windy means there is a lot of wind — not necessarily cold.'},
                {'afirmacion': 'We wear boots when it snows.', 'respuesta': True, 'explicacion': 'Yes! Boots protect our feet from snow and rain.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Tiempo cálido', 'emoji': '☀️', 'items': ['sunny', 'hot', 'warm', 'humid']},
                {'nombre': 'Tiempo frío', 'emoji': '❄️', 'items': ['cold', 'snowy', 'windy', 'rainy', 'cloudy']},
            ]},
            {'categorias': [
                {'nombre': 'Estaciones cálidas', 'emoji': '🌸', 'items': ['spring', 'summer']},
                {'nombre': 'Estaciones frías', 'emoji': '🍂', 'items': ['fall', 'autumn', 'winter']},
            ]},
            {'categorias': [
                {'nombre': 'Ropa para frío', 'emoji': '🧥', 'items': ['coat', 'boots', 'sweater', 'scarf', 'gloves']},
                {'nombre': 'Ropa para calor', 'emoji': '👙', 'items': ['sandals', 'sunglasses', 'shorts', 'hat']},
            ]},
        ],
    },
    9: {  # Mis Actividades Favoritas — D4
        'ordenar_oracion': [
            {'oraciones': ['I play soccer on Saturdays', 'My team wins every game', 'Soccer is my favorite sport']},
            {'oraciones': ['She reads books every evening', 'I love drawing animals', 'Music is great for everyone']},
            {'oraciones': ['On Monday I go to school', 'After school I do my homework', 'I sleep at nine oclock']},
            {'oraciones': ['I play video games on weekends', 'My hobby is cooking with mom', 'Dancing is a lot of fun']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I play ___ every Saturday.', 'respuesta': 'soccer', 'emoji': '⚽'},
                {'texto': 'She loves ___ books.', 'respuesta': 'reading', 'emoji': '📚'},
                {'texto': 'Monday is the first day of the ___.', 'respuesta': 'week', 'emoji': '📅'},
            ]},
            {'oraciones': [
                {'texto': 'I ___ my homework after school.', 'respuesta': 'do', 'emoji': '📝'},
                {'texto': 'Basketball is a team ___.', 'respuesta': 'sport', 'emoji': '🏀'},
                {'texto': 'I go to ___ on weekdays.', 'respuesta': 'school', 'emoji': '🏫'},
            ]},
            {'oraciones': [
                {'texto': 'My favorite ___ is swimming.', 'respuesta': 'sport', 'emoji': '🏊'},
                {'texto': 'I love ___ to music.', 'respuesta': 'listening', 'emoji': '🎵'},
                {'texto': 'She ___ very well.', 'respuesta': 'dances', 'emoji': '💃'},
            ]},
            {'oraciones': [
                {'texto': 'After school I ___ with my friends.', 'respuesta': 'play', 'emoji': '🎮'},
                {'texto': 'I eat ___ with my family.', 'respuesta': 'dinner', 'emoji': '🍽️'},
                {'texto': 'On ___ we rest and play.', 'respuesta': 'weekends', 'emoji': '🎉'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'Soccer is played with a round ball.', 'respuesta': True, 'explicacion': 'Yes! Soccer is played with a round ball on a grass field.'},
                {'afirmacion': 'Monday is the last day of the week.', 'respuesta': False, 'explicacion': 'Monday is the first day of the week.'},
                {'afirmacion': 'Reading is a hobby.', 'respuesta': True, 'explicacion': 'Yes! Reading books, drawing, and dancing are all hobbies.'},
                {'afirmacion': 'We do homework in the swimming pool.', 'respuesta': False, 'explicacion': 'We do homework at home or school, not in a pool!'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Friday is before Saturday.', 'respuesta': True, 'explicacion': 'Correct! Friday → Saturday → Sunday.'},
                {'afirmacion': 'Swimming is a land sport.', 'respuesta': False, 'explicacion': 'Swimming is a water sport!'},
                {'afirmacion': 'Dancing is a fun activity.', 'respuesta': True, 'explicacion': 'Yes! Dancing is a great way to have fun and exercise.'},
                {'afirmacion': 'The weekend has five days.', 'respuesta': False, 'explicacion': 'The weekend is only Saturday and Sunday — two days!'},
            ]},
            {'preguntas': [
                {'afirmacion': 'Basketball is played with a hoop.', 'respuesta': True, 'explicacion': 'Yes! In basketball, you throw the ball into a hoop to score.'},
                {'afirmacion': '"After school" means before school.', 'respuesta': False, 'explicacion': '"After school" means when school is over, not before!'},
                {'afirmacion': 'A hobby is something you enjoy doing.', 'respuesta': True, 'explicacion': 'Yes! A hobby is an activity you do for fun in your free time.'},
                {'afirmacion': 'Wednesday comes after Thursday.', 'respuesta': False, 'explicacion': 'Wednesday comes BEFORE Thursday.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Deportes en equipo', 'emoji': '⚽', 'items': ['soccer', 'basketball', 'baseball', 'volleyball']},
                {'nombre': 'Deportes individuales', 'emoji': '🏊', 'items': ['swimming', 'cycling', 'gymnastics', 'running', 'tennis']},
            ]},
            {'categorias': [
                {'nombre': 'Días de semana', 'emoji': '📚', 'items': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']},
                {'nombre': 'Fin de semana', 'emoji': '🎉', 'items': ['Saturday', 'Sunday']},
            ]},
            {'categorias': [
                {'nombre': 'Actividades artísticas', 'emoji': '🎨', 'items': ['drawing', 'painting', 'singing', 'dancing', 'playing music']},
                {'nombre': 'Actividades deportivas', 'emoji': '🏃', 'items': ['soccer', 'swimming', 'cycling', 'running', 'basketball']},
            ]},
        ],
    },
    10: {  # Mi Pueblo, Mi Mundo — D4
        'ordenar_oracion': [
            {'oraciones': ['The school is near the park', 'I walk to school every morning', 'My neighborhood is very safe']},
            {'oraciones': ['Turn left at the traffic light', 'Go straight for two blocks', 'The hospital is on the right']},
            {'oraciones': ['I take the bus to school', 'The market is very busy today', 'My town has many people']},
            {'oraciones': ['The library is next to the bank', 'We live in a beautiful city', 'Our community helps each other']},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I go to ___ every day to learn.', 'respuesta': 'school', 'emoji': '🏫'},
                {'texto': 'We buy food at the ___.', 'respuesta': 'market', 'emoji': '🛒'},
                {'texto': 'Sick people go to the ___.', 'respuesta': 'hospital', 'emoji': '🏥'},
            ]},
            {'oraciones': [
                {'texto': '___ left and you will see the park.', 'respuesta': 'Turn', 'emoji': '⬅️'},
                {'texto': 'Go ___ for two blocks.', 'respuesta': 'straight', 'emoji': '⬆️'},
                {'texto': 'The school is ___ the park.', 'respuesta': 'near', 'emoji': '📍'},
            ]},
            {'oraciones': [
                {'texto': 'I take the ___ to get to school.', 'respuesta': 'bus', 'emoji': '🚌'},
                {'texto': 'My ___ is a friendly place to live.', 'respuesta': 'neighborhood', 'emoji': '🏘️'},
                {'texto': 'We borrow books from the ___.', 'respuesta': 'library', 'emoji': '📚'},
            ]},
            {'oraciones': [
                {'texto': 'I ride my ___ to the park.', 'respuesta': 'bicycle', 'emoji': '🚲'},
                {'texto': 'Our ___ helps people feel safe.', 'respuesta': 'community', 'emoji': '🏘️'},
                {'texto': 'The ___ is very busy in the morning.', 'respuesta': 'street', 'emoji': '🛣️'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'A school is where we learn.', 'respuesta': True, 'explicacion': 'Yes! We go to school to study and learn new things.'},
                {'afirmacion': 'A hospital is where we buy food.', 'respuesta': False, 'explicacion': 'We go to a hospital when we are sick. We buy food at a market!'},
                {'afirmacion': '"Turn left" means girar a la izquierda.', 'respuesta': True, 'explicacion': 'Correct! Turn left = girar a la izquierda.'},
                {'afirmacion': 'A bus is a type of transportation.', 'respuesta': True, 'explicacion': 'Yes! Buses, cars, and bikes are all transportation.'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A library is full of books.', 'respuesta': True, 'explicacion': 'Yes! Libraries have many books that you can borrow.'},
                {'afirmacion': '"Go straight" means turn right.', 'respuesta': False, 'explicacion': '"Go straight" means seguir derecho. Turn right = girar a la derecha.'},
                {'afirmacion': 'A community is a group of people living together.', 'respuesta': True, 'explicacion': 'Yes! A community is a group of neighbors and families.'},
                {'afirmacion': 'A bicycle has four wheels.', 'respuesta': False, 'explicacion': 'A bicycle has two wheels, not four!'},
            ]},
            {'preguntas': [
                {'afirmacion': 'A park is a good place to play.', 'respuesta': True, 'explicacion': 'Yes! Parks have grass and space to play.'},
                {'afirmacion': '"Near" means lejos in Spanish.', 'respuesta': False, 'explicacion': '"Near" means cerca. "Far" means lejos.'},
                {'afirmacion': 'A neighborhood is part of a city.', 'respuesta': True, 'explicacion': 'Yes! A city is made up of many neighborhoods.'},
                {'afirmacion': 'A taxi is the same as a bus.', 'respuesta': False, 'explicacion': 'A taxi is a small private car. A bus carries many people.'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Lugares del pueblo', 'emoji': '🏘️', 'items': ['school', 'park', 'market', 'hospital', 'library', 'church']},
                {'nombre': 'Medios de transporte', 'emoji': '🚌', 'items': ['bus', 'car', 'bicycle', 'motorcycle', 'taxi', 'on foot']},
            ]},
            {'categorias': [
                {'nombre': 'Direcciones', 'emoji': '🗺️', 'items': ['turn left', 'turn right', 'go straight', 'stop', 'near', 'far']},
                {'nombre': 'Comunidad', 'emoji': '🏘️', 'items': ['neighbor', 'community', 'street', 'neighborhood', 'town', 'city']},
            ]},
            {'categorias': [
                {'nombre': 'Transporte público', 'emoji': '🚌', 'items': ['bus', 'taxi', 'train', 'metro']},
                {'nombre': 'Transporte privado', 'emoji': '🚗', 'items': ['car', 'bicycle', 'motorcycle', 'on foot']},
            ]},
        ],
    },
}


def _make_variantes_memoria(vocab, max_pares):
    """Auto-generate 3 memoria variants by rotating through vocabulary subsets."""
    variantes = []
    n = len(vocab)
    for start in range(3):
        subset = [vocab[(start * 2 + i) % n] for i in range(min(max_pares, n))]
        pares = [{'es': w['es'], 'en': w['en'], 'emoji': w.get('emoji', '📝')} for w in subset]
        variantes.append({'pares': pares})
    return variantes


def _make_variantes_unir(vocab, max_pares):
    """Auto-generate 3 unir_pares variants by rotating through vocabulary subsets."""
    variantes = []
    n = len(vocab)
    for start in range(3):
        subset = [vocab[(start * 2 + i) % n] for i in range(min(max_pares, n))]
        pares = [{'izq': w['es'], 'der': f"{w.get('emoji', '📝')} {w['en']}"} for w in subset]
        variantes.append({'pares': pares})
    return variantes


def _escalar_variantes(tipo, dificultad, variantes):
    """Trim content arrays inside each variant to match the difficulty level."""
    max_items = DIFFICULTY_PARAMS.get(tipo, {}).get(dificultad)
    if max_items is None:
        return variantes
    resultado = []
    for v in variantes:
        v2 = dict(v)
        if tipo in ('memoria', 'unir_pares') and 'pares' in v2:
            v2['pares'] = v2['pares'][:max_items]
        elif tipo == 'verdadero_falso' and 'preguntas' in v2:
            v2['preguntas'] = v2['preguntas'][:max_items]
        elif tipo == 'rellenar' and 'oraciones' in v2:
            v2['oraciones'] = v2['oraciones'][:max_items]
        elif tipo == 'ordenar_oracion' and 'oraciones' in v2:
            v2['oraciones'] = v2['oraciones'][:max_items]
        resultado.append(v2)
    return resultado


def _make_variantes(tipo, seccion_pk, vocab, dificultad):
    """Return the variantes list for a given tipo, section, and difficulty."""
    if tipo == 'memoria':
        return _make_variantes_memoria(vocab, DIFFICULTY_PARAMS['memoria'][dificultad])
    if tipo == 'unir_pares':
        return _make_variantes_unir(vocab, DIFFICULTY_PARAMS['unir_pares'][dificultad])
    sec_content = MINIJUEGO_CONTENT.get(seccion_pk, {})
    variantes = sec_content.get(tipo, [])
    if not variantes:
        return _make_variantes_memoria(vocab, DIFFICULTY_PARAMS['memoria'][dificultad])
    return _escalar_variantes(tipo, dificultad, variantes)


def _make_minijuego_embed(seccion_pk, leccion_global_idx, vocab, dificultad):
    """Generate the minijuego_embed activity dict for a lesson."""
    tipo = TIPO_ROTATION[leccion_global_idx % len(TIPO_ROTATION)]
    variantes = _make_variantes(tipo, seccion_pk, vocab, dificultad)
    return {
        "orden": 8,
        "tipo": "minijuego_embed",
        "puntos_actividad": 3,
        "datos": {
            "titulo": TITULOS_MINIJUEGO[tipo],
            "tipo_minijuego": tipo,
            "instruccion": INSTRUCCIONES_MINIJUEGO[tipo],
            "variantes": variantes,
        },
    }


class Command(BaseCommand):
    help = 'Generate Historia mode fixture with sections, lessons, and activities.'

    def handle(self, *args, **options):
        fixture = []
        leccion_pk = 0
        actividad_pk = 0
        leccion_global_idx = 0  # 0-based counter across all lessons for tipo rotation

        # SeccionHistoria records
        for sec in SECCIONES:
            fields = {
                "titulo": sec["titulo"],
                "descripcion": sec.get("descripcion", ""),
                "orden": sec["orden"],
                "icono_emoji": sec["icono_emoji"],
                "color_hex": sec["color_hex"],
                "is_desbloqueada_por_defecto": sec.get("is_desbloqueada_por_defecto", False),
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
            fixture.append({"model": "historia.seccionhistoria", "pk": sec["pk"], "fields": fields})

        # Leccion + ActividadLeccion records
        for sec in SECCIONES:
            sec_pk = sec["pk"]
            dificultad = get_dificultad(sec["orden"])
            lecciones = LECCIONES_POR_SECCION[sec_pk]
            for orden_idx, lec in enumerate(lecciones, start=1):
                leccion_pk += 1
                is_repaso = lec.get("is_repaso", False)
                leccion_fields = {
                    "seccion": sec_pk,
                    "titulo": lec["titulo"],
                    "descripcion_corta": lec["descripcion_corta"],
                    "orden": orden_idx,
                    "puntos_xp": lec["puntos_xp"],
                    "huesos_recompensa": lec["huesos_recompensa"],
                    "tiempo_estimado_minutos": lec["tiempo_estimado_minutos"],
                    "icono_emoji": lec["icono_emoji"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
                fixture.append({"model": "historia.leccion", "pk": leccion_pk, "fields": leccion_fields})

                # Build activities
                vocab = VOCABULARIO.get((sec_pk, orden_idx), [])
                if not vocab:
                    # fallback minimal vocab
                    vocab = [
                        {"es": "palabra", "en": "word", "emoji": "📝"},
                        {"es": "frase", "en": "phrase", "emoji": "💬"},
                        {"es": "letra", "en": "letter", "emoji": "🔤"},
                        {"es": "idioma", "en": "language", "emoji": "🌐"},
                        {"es": "inglés", "en": "English", "emoji": "🇬🇧"},
                        {"es": "español", "en": "Spanish", "emoji": "🇨🇴"},
                    ]

                tema_es = lec["titulo"]
                tema_en = lec["titulo"]

                actividades = make_actividades(
                    tema_es, tema_en, vocab, sec["titulo"],
                    seccion_pk=sec_pk,
                    leccion_global_idx=leccion_global_idx,
                    dificultad=dificultad,
                    is_repaso=is_repaso,
                )
                leccion_global_idx += 1

                for act in actividades:
                    actividad_pk += 1
                    act_fields = {
                        "leccion": leccion_pk,
                        "orden": act["orden"],
                        "tipo": act["tipo"],
                        "datos": act["datos"],
                        "puntos_actividad": act["puntos_actividad"],
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                    fixture.append({"model": "historia.actividadleccion", "pk": actividad_pk, "fields": act_fields})

        out_path = BASE_DIR / "apps" / "historia" / "fixtures" / "modo_historia.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fixture, f, ensure_ascii=False, indent=2)

        total_secciones = sum(1 for r in fixture if r["model"] == "historia.seccionhistoria")
        total_lecciones = sum(1 for r in fixture if r["model"] == "historia.leccion")
        total_actividades = sum(1 for r in fixture if r["model"] == "historia.actividadleccion")

        self.stdout.write(self.style.SUCCESS(
            f"Fixture generated: {out_path}\n"
            f"  Secciones:   {total_secciones}\n"
            f"  Lecciones:   {total_lecciones}\n"
            f"  Actividades: {total_actividades}"
        ))
