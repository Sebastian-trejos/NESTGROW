import random


MILO_MESSAGES = [
    {"text": "Hi! I'm Milo 🐺 I'm here to help you learn English!", "mood": "happy"},
    {"text": "You can do it! Every exercise makes you smarter. 💪", "mood": "encouraging"},
    {"text": "Wow, you're doing great! Keep it up! ⭐", "mood": "excited"},
    {"text": "Remember: learning English is fun when you play. Let's go! 🎮", "mood": "playful"},
    {"text": "You're a champion! One step at a time... you've got this! 🏆", "mood": "proud"},
    {"text": "Practice every day and you'll be amazed how much you learn! 📚", "mood": "wise"},
    {"text": "Mistakes are part of learning! Don't give up. 🌟", "mood": "supportive"},
    {"text": "Incredible! Every new word you learn is a superpower. ✨", "mood": "excited"},
]

MILO_GREETINGS = [
    "Hello, explorer!",
    "Welcome back!",
    "Great to see you!",
    "Time to learn!",
    "Ready to play!",
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
