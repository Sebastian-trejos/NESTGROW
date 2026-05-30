import os
import unicodedata

from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, ActiveModel


# ── Static image resolution ────────────────────────────────────────────────────

# Maps vocabulary words (normalized) to the image filename stem (no extension, no path).
# Handles: number words → digit filenames, English color → Spanish image name, etc.
_WORD_ALIASES = {
    # ── Números en inglés → dígito ──────────────────────────────────────────
    'one': '1',      'two': '2',      'three': '3',    'four': '4',
    'five': '5',     'six': '6',      'seven': '7',    'eight': '8',
    'nine': '9',     'ten': '10',     'eleven': '11',  'twelve': '12',
    'thirteen': '13','fourteen': '14','fifteen': '15', 'sixteen': '16',
    'seventeen': '17','eighteen': '18','nineteen': '19','twenty': '20',
    'thirty': '30',  'forty': '40',   'fifty': '50',   'sixty': '60',
    'seventy': '70', 'eighty': '80',  'ninety': '90',
    'one hundred': '100', 'hundred': '100',
    'one thousand': '1000', 'thousand': '1000',
    # ── Números en español → dígito ─────────────────────────────────────────
    'uno': '1',   'dos': '2',   'tres': '3',  'cuatro': '4', 'cinco': '5',
    'seis': '6',  'siete': '7', 'ocho': '8',  'nueve': '9',  'diez': '10',
    'once': '11', 'doce': '12', 'trece': '13','catorce': '14','quince': '15',
    'dieciseis': '16', 'diecisiete': '17', 'dieciocho': '18', 'diecinueve': '19',
    'veinte': '20', 'treinta': '30', 'cuarenta': '40', 'cincuenta': '50',
    'sesenta': '60','setenta': '70', 'ochenta': '80',  'noventa': '90',
    'cien': '100', 'ciento': '100', 'mil': '1000',
    # ── Colores en inglés → nombre de archivo (en español) ──────────────────
    'red': 'rojo',     'blue': 'azul',      'green': 'verde',
    'yellow': 'amarillo','orange': 'naranja','purple': 'morado',
    'pink': 'rosa',    'white': 'blanco',   'black': 'negro',
    'gray': 'gris',    'grey': 'gris',      'brown': 'cafe',
    'cyan': 'cian',    'indigo': 'indigo',  'magenta': 'magenta',
    'scarlet': 'escarlata','turquoise': 'turquesa',
    'gold': 'oro',     'silver': 'plateado','violet': 'violeta',
    # ── Singular/plural o diferencias de nombre en el archivo ────────────────
    'grape': 'grapes',         'uva': 'grapes',
    'lip': 'lips',             'labio': 'lips',
    'stomach': 'stomatch',     'estomago': 'stomatch',   # typo en el filename
    'police officer': 'police','policia': 'police',      'policeman': 'police',
    'pajamas': 'pajama',       'pijama': 'pajama',
    'hot air balloon': 'hotairballon',
    'globo aerostatico': 'hotairballon',
    'father': 'padre2',        'papa': 'padre2',
    'aunt': 'abuela',          'tia': 'abuela',          # fallback aproximado
    'deer': 'venado',          'ciervo': 'venado',
    'duck': 'pajaro2',         'pato': 'pajaro2',
    # ── Animales en inglés → archivo en español ──────────────────────────────
    'butterfly': 'mariposa', 'frog': 'rana',     'snake': 'serpiente',
    'horse': 'caballo',      'rabbit': 'conejo', 'bear': 'oso',
    'wolf': 'lobo',          'fox': 'zorro',     'cow': 'vaca',
    'pig': 'cerdo',          'sheep': 'oveja',   'bird': 'pajaro',
    'fish': 'pez',           'shark': 'tiburon', 'whale': 'ballena',
    'dolphin': 'delfin',     'crocodile': 'cocodrilo', 'giraffe': 'jirafa',
    'zebra': 'cebra',        'kangaroo': 'canguro', 'monkey': 'mono',
    'penguin': 'pinguino',   'tiger': 'tigre',   'bull': 'toro',
    'parrot': 'loro',        'panda': 'panda',   'dragonfly': 'libelula',
    'snail': 'caracol',      'crab': 'cangrejo', 'flamingo': 'flamenco',
    'hamster': 'hamster',    'octopus': 'pulpo', 'ladybug': 'mariquita',
    'turtle': 'tortuga',     'lion': 'leon',     'elephant': 'elefante',
    'cat': 'gato',           'dog': 'perro',
    # ── Familia ──────────────────────────────────────────────────────────────
    'grandmother': 'abuela', 'grandfather': 'abuelo', 'grandparents': 'abuelos',
    'baby': 'bebe',          'mother': 'mama',          'mom': 'mama',
    'daughter': 'hija',      'son': 'hijo',
    'siblings': 'hermanos',  'brother': 'hermanos',     'sister': 'hermanos',
    'boy': 'nino',           'girl': 'nina',
    # ── Transporte en inglés → archivos mixtos ────────────────────────────────
    'airplane': 'airplane',  'plane': 'airplane',
    'hot air balloon': 'hotairballon',
    'subway': 'metro',       'pickup truck': 'pickup',
    # ── Ropa singular vs plural u otros nombres ───────────────────────────────
    't-shirt': 'T-Shirt',    'tshirt': 'T-Shirt',   'shirt': 'T-Shirt',
    'pajama': 'pajama',
    # ── Comida ───────────────────────────────────────────────────────────────
    'bread': 'pan',          'rice': 'arroz',       'water': 'agua',
    'milk': 'leche',         'egg': 'huevo',        'sugar': 'azucar',
    'salt': 'sal',           'butter': 'mantequilla','honey': 'miel',
    'cheese': 'queso',       'chicken': 'pollo',    'salad': 'ensalada',
    'soup': 'sopa',          'cookie': 'galleta',   'cake': 'pastel',
    'chocolate': 'chocolate','ice cream': 'helado', 'lemonade': 'limonada',
    'tea': 'te',             'food': 'comida',
    'hamburger': 'hamburguesa', 'sandwich': 'sandwich',
    'pizza': 'pizza',        'pasta': 'pasta',      'coffee': 'cafe',
    # ── Partes del cuerpo ────────────────────────────────────────────────────
    'arm': 'Arm',   'back': 'Back',   'chest': 'Chest', 'ear': 'Ear',
    'eye': 'Eye',   'finger': 'Finger','foot': 'Foot',  'hair': 'Hair',
    'hand': 'Hand', 'head': 'Head',   'knee': 'Knee',   'leg': 'Leg',
    'lips': 'Lips', 'mouth': 'Mouth', 'neck': 'Neck',   'nose': 'Nose',
    'shoulder': 'Shoulder', 'teeth': 'Teeth', 'tongue': 'Tongue',
    'heart': 'Heart',
    # ── Formas ───────────────────────────────────────────────────────────────
    'circle': 'circle','square': 'square','triangle': 'triangle',
    'rectangle': 'rectangle','oval': 'oval','diamond': 'diamond',
    'star': 'star','hexagon': 'hexagon','pentagon': 'pentagon',
    'cross': 'cross','arrow': 'arrow',
    # ── Acciones → imágenes de Milo (1 imagen por palabra, sin repetir) ─────
    'run': 'milo_corriendo',      'correr': 'milo_corriendo',
    'dance': 'milo_bai',          'bailar': 'milo_bai',
    'jump': 'milo_emociontotal',  'saltar': 'milo_emociontotal',
    'laugh': 'milo_carcajadas',   'reir': 'milo_carcajadas',
    'cry': 'milo_llorando',       'llorar': 'milo_llorando',
    'read': 'milo_leyendo1',      'leer': 'milo_leyendo1',
    'learn': 'milo_leyendo2',     'aprender': 'milo_leyendo2',
    'teach': 'milo_apuntes',      'ensenar': 'milo_apuntes',
    'write': 'milo_star',         'escribir': 'milo_star',
    'draw': 'milo_pintor',        'dibujar': 'milo_pintor',
    'talk': 'milo_hablando',      'hablar': 'milo_hablando',
    'listen': 'milo_susurrando',  'escuchar': 'milo_susurrando',
    'eat': 'milo_hueso',          'comer': 'milo_hueso',
    'sleep': 'milo_durmiendo',    'dormir': 'milo_durmiendo',
    'think': 'milo_duda1',        'pensar': 'milo_duda1',
    'watch': 'milo_lupa1',        'ver': 'milo_lupa1',
    'play': 'milo_fest2',         'jugar': 'milo_fest2',
    # ── Adjetivos → imágenes de Milo (1 imagen por palabra, sin repetir) ────
    'good': 'milo_pulgar',        'bueno': 'milo_pulgar',
    'bad': 'milo_enojado2',       'malo': 'milo_enojado2',
    'strong': 'milo_orgulloso',   'fuerte': 'milo_orgulloso',
    'beautiful': 'milo_asombrado2','hermoso': 'milo_asombrado2',
}

_STATIC_IMG_MAP = None  # populated on first call


def _normalize(s):
    """Lowercase, strip accents, replace underscores with spaces."""
    s = s.lower().strip().replace('_', ' ')
    # Remove combining diacritical marks (accents)
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def _build_static_img_map():
    """Scan STATICFILES_DIRS/img/ once and build a normalized lookup dict."""
    img_map = {}
    for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
        img_dir = os.path.join(static_dir, 'img')
        if os.path.isdir(img_dir):
            for fname in os.listdir(img_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    stem = os.path.splitext(fname)[0]
                    img_map[_normalize(stem)] = f'img/{fname}'
    return img_map


def _resolve_static_image(word_en, word_es):
    """Return a static URL for the vocabulary word, or None if no match found."""
    global _STATIC_IMG_MAP
    if _STATIC_IMG_MAP is None:
        _STATIC_IMG_MAP = _build_static_img_map()

    from django.templatetags.static import static as _static

    candidates_raw = [
        word_en.strip() if word_en else '',
        word_es.strip() if word_es else '',
    ]

    checked = []
    for raw in candidates_raw:
        if not raw:
            continue
        norm = _normalize(raw)
        checked.append(norm)

        # Direct match (e.g. "airport" → Airport.png, "perro" → perro.png)
        if norm in _STATIC_IMG_MAP:
            return _static(_STATIC_IMG_MAP[norm])

        # Alias match (e.g. "one" → "1" → 1.png, "red" → "rojo" → rojo.png)
        alias = _normalize(_WORD_ALIASES.get(norm, ''))
        if alias and alias in _STATIC_IMG_MAP:
            return _static(_STATIC_IMG_MAP[alias])

    return None


class Category(TimeStampedModel, ActiveModel):
    """Vocabulary category / topic (Animals, Colors, Numbers, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nombre (Español)')
    name_en = models.CharField(max_length=100, verbose_name='Nombre (Inglés)')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🐾')
    color = models.CharField(max_length=7, default='#6C63FF',
                             help_text='Color HEX para la tarjeta (ej: #FF6B6B)')
    order = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name} / {self.name_en}"


class VocabularyItem(TimeStampedModel, ActiveModel):
    """A single vocabulary word with image and audio."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vocabulary')
    word_es = models.CharField(max_length=100, verbose_name='Palabra en Español')
    word_en = models.CharField(max_length=100, verbose_name='Word in English')
    descripcion_es = models.TextField(blank=True, verbose_name='Descripción en español',
                                      help_text='Definición sencilla en español para el estudiante')
    pronunciacion_es = models.CharField(max_length=150, blank=True,
                                        verbose_name='Pronunciación aproximada',
                                        help_text='Ej: "dog" se pronuncia "dag"')
    image = models.ImageField(upload_to='vocabulary/images/', blank=True, null=True)
    audio = models.FileField(upload_to='vocabulary/audio/', blank=True, null=True,
                             help_text='Archivo .mp3 con la pronunciación en inglés')
    emoji = models.CharField(max_length=10, blank=True, default='',
                             verbose_name='Emoji representativo',
                             help_text='Emoji individual de la palabra (ej: 🐕 para Dog)')
    hint = models.CharField(max_length=200, blank=True,
                            verbose_name='Pista o contexto')
    difficulty = models.IntegerField(
        default=1, choices=[(1, 'Fácil'), (2, 'Medio'), (3, 'Difícil')]
    )
    is_unlocked_by_default = models.BooleanField(
        default=False, verbose_name='Desbloqueada por defecto',
        help_text='True = visible para todos los estudiantes sin completar nada'
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden dentro de categoría')

    class Meta:
        verbose_name = 'Vocabulario'
        verbose_name_plural = 'Vocabulario'
        ordering = ['orden', 'word_en']

    @property
    def display_image_url(self):
        """Image URL with priority: uploaded image → static library match → None."""
        if self.image:
            return self.image.url
        return _resolve_static_image(self.word_en, self.word_es)

    def __str__(self):
        return f"{self.word_en} / {self.word_es} ({self.category.name})"


class VocabularioDesbloqueado(models.Model):
    """Registro de qué palabras ha desbloqueado cada estudiante."""
    FUENTE_CHOICES = [
        ('inicial', 'Inicial'),
        ('taller', 'Taller'),
        ('minijuego', 'Minijuego'),
        ('historia', 'Modo Historia'),
    ]
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='vocabulario_desbloqueado'
    )
    item = models.ForeignKey(
        VocabularyItem, on_delete=models.CASCADE,
        related_name='desbloqueado_por'
    )
    desbloqueado_en = models.DateTimeField(auto_now_add=True)
    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, default='inicial')

    class Meta:
        verbose_name = 'Vocabulario Desbloqueado'
        verbose_name_plural = 'Vocabulario Desbloqueado'
        unique_together = [('estudiante', 'item')]
        ordering = ['-desbloqueado_en']

    def __str__(self):
        return f"{self.estudiante.username} → {self.item.word_en}"


class HitoVocabulario(models.Model):
    """Hito de vocabulario desbloqueado — otorga huesos al alcanzar N palabras."""
    HITOS = [(10, 2), (25, 5), (50, 10), (100, 20), (200, 40)]

    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='hitos_vocabulario'
    )
    palabras_cantidad = models.IntegerField(verbose_name='Palabras al alcanzar el hito')
    huesos_ganados = models.IntegerField(verbose_name='Huesos otorgados')
    entregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hito de Vocabulario'
        verbose_name_plural = 'Hitos de Vocabulario'
        unique_together = [('estudiante', 'palabras_cantidad')]
        ordering = ['palabras_cantidad']

    def __str__(self):
        return f"{self.estudiante.username} — {self.palabras_cantidad} palabras → {self.huesos_ganados} 🦴"
