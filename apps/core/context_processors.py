import random


MILO_MESSAGES = [
    {"text": "¡Hola! Soy Milo 🐺 ¡Estoy aquí para ayudarte a aprender inglés!", "mood": "happy"},
    {"text": "¡Tú puedes lograrlo! Cada ejercicio te hace más inteligente. 💪", "mood": "encouraging"},
    {"text": "¡Wow, qué bien lo estás haciendo! ¡Sigue así! ⭐", "mood": "excited"},
    {"text": "Recuerda: aprender inglés es divertido cuando juegas. ¡Vamos! 🎮", "mood": "playful"},
    {"text": "¡Eres un campeón! Un paso a la vez... ¡tú puedes! 🏆", "mood": "proud"},
    {"text": "¡Practica todos los días y verás cuánto aprendes! 📚", "mood": "wise"},
    {"text": "¡Los errores también son aprendizaje! No te rindas. 🌟", "mood": "supportive"},
    {"text": "¡Increíble! Cada palabra nueva que aprendes es un superpoder. ✨", "mood": "excited"},
]

MILO_GREETINGS = [
    "¡Hola, explorador!",
    "¡Bienvenido de vuelta!",
    "¡Qué bueno verte!",
    "¡Es hora de aprender!",
    "¡Listo para jugar!",
]


def milo_messages(request):
    """Provides Milo's messages globally to all templates."""
    return {
        'milo_message': random.choice(MILO_MESSAGES),
        'milo_greeting': random.choice(MILO_GREETINGS),
        'all_milo_messages': MILO_MESSAGES,
    }


def global_context(request):
    """Global context available in all templates."""
    ctx = {
        'app_name': 'NestGrow',
        'app_slogan': 'Aprende inglés jugando',
    }
    if request.user.is_authenticated:
        ctx['user_role'] = getattr(request.user, 'role', 'estudiante')
    return ctx
