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
def make_actividades(tema_es, tema_en, vocabulario, seccion_titulo, is_repaso=False):
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
        {
            "orden": 8,
            "tipo": "minijuego_embed",
            "puntos_actividad": 3,
            "datos": {
                "titulo": "¡Minijuego!",
                "tipo_minijuego": "memoria",
                "instruccion": "Match each word with its image.",
                "pares": [{"es": w["es"], "en": w["en"], "emoji": w.get("emoji", "📝")} for w in v[:6]],
            },
        },
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


class Command(BaseCommand):
    help = 'Generate Historia mode fixture with sections, lessons, and activities.'

    def handle(self, *args, **options):
        fixture = []
        leccion_pk = 0
        actividad_pk = 0

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

                actividades = make_actividades(tema_es, tema_en, vocab, sec["titulo"], is_repaso=is_repaso)

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
