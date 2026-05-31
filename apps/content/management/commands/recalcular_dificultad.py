"""
Recalcula el campo `difficulty` de todos los VocabularyItem según:
  - Longitud de la palabra en inglés (letras)
  - Dificultad de pronunciación para hispanohablantes

Uso:
    python manage.py recalcular_dificultad
    python manage.py recalcular_dificultad --dry-run   ← solo muestra, no guarda
"""

import re
from django.core.management.base import BaseCommand
from apps.content.models import VocabularyItem


# Palabras con pronunciación especialmente irregular para hispanohablantes
OVERRIDES = {
    # Vocales + letras silenciosas muy irregulares
    'knee': 2,       # kn- silenciosa
    'knife': 2,
    'knight': 3,     # kn- + ght
    'know': 2,
    'kneel': 2,
    'write': 2,      # wr- silenciosa
    'wrist': 2,
    'wrap': 2,
    'wrong': 2,
    'eight': 2,      # -igh-
    'weigh': 2,
    'weight': 2,
    'height': 2,
    'two': 2,        # w silenciosa
    'whole': 2,
    'laugh': 2,      # augh → /æf/
    'cough': 2,
    'though': 2,     # ough → /oʊ/
    'through': 3,    # th + ough irregular
    'Wednesday': 3,  # d silenciosa + pronunciación irregular
    'february': 3,   # primera r generalmente silenciosa
    'queue': 2,
    'eye': 2,        # spelling muy irregular
    'colonel': 3,    # pronunciación /kɜːrnəl/
    # Vocales compuestas
    'beautiful': 3,  # eau + iful
    'choir': 2,
    # Sonidos que no existen en español y son palabras cortas
    'the': 1,        # muy común, aunque tiene /ð/
    'three': 2,      # th + vocal
    'there': 2,
    'them': 1,
    'they': 1,
    'think': 2,
    'this': 1,
    'that': 1,
    'thumb': 2,      # mb final silenciosa
    'lamb': 2,
    'comb': 2,
}


def _difficulty(word_en: str) -> int:
    """
    Devuelve 1 (Fácil), 2 (Medio) o 3 (Difícil).

    Criterios:
    1. Longitud: número total de letras (sin espacios ni puntuación).
       ≤3 → 0 pts | 4-5 → 1 | 6-7 → 2 | 8-9 → 3 | 10+ → 4
    2. Pronunciación (bonus pts para hispanohablantes):
       - Patrón kn- al inicio: +2
       - Patrón wr- al inicio: +2
       - -mb al final de sílaba: +1
       - -ght-: +1
       - ough: +2  (through, cough, though, tough)
       - augh: +2  (laugh, caught)
       - ph → /f/: +1
       - eau: +1
       - th: +1
       - Entrada multi-palabra (frase): +1
    3. Umbrales finales:
       total 0-1 → 1 (Fácil)
       total 2-3 → 2 (Medio)
       total 4+  → 3 (Difícil)
    """
    key = word_en.lower().strip()

    # Override manual
    if key in OVERRIDES:
        return OVERRIDES[key]

    # Letras solo (sin espacios, guiones, números)
    only_letters = re.sub(r'[^a-z]', '', key)
    length = len(only_letters)

    # Puntuación por longitud
    if length <= 3:
        length_pts = 0
    elif length <= 5:
        length_pts = 1
    elif length <= 7:
        length_pts = 2
    elif length <= 9:
        length_pts = 3
    else:
        length_pts = 4

    # Puntuación por pronunciación
    prn = 0

    # Letras silenciosas iniciales
    if re.search(r'\bkn', key):
        prn += 2
    if re.search(r'\bwr', key):
        prn += 2

    # -mb al final de palabra
    if re.search(r'mb\b', key):
        prn += 1

    # Grupo -ght-
    if 'ght' in key:
        prn += 1

    # Patrones ough / augh (muy irregulares)
    if 'ough' in key:
        prn += 2
    elif 'augh' in key:
        prn += 2

    # ph como /f/
    if 'ph' in key:
        prn += 1

    # eau (beautiful, beau…)
    if 'eau' in key:
        prn += 1

    # Sonido /θ/ o /ð/ inexistente en español
    if 'th' in key:
        prn += 1

    # Sonido /ʃ/ (sh) — no existe en español estándar
    if 'sh' in key:
        prn += 1

    # Sonido /w/ de "wh" — diferente a "gu-" español
    if re.search(r'\bwh', key):
        prn += 1

    # Entrada multi-palabra (frases o palabras compuestas con espacio)
    if ' ' in word_en.strip():
        prn += 1

    total = length_pts + prn

    if total <= 1:
        return 1
    elif total <= 3:
        return 2
    else:
        return 3


class Command(BaseCommand):
    help = 'Recalcula la dificultad de cada VocabularyItem según longitud y pronunciación.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra los cambios sin guardar en la base de datos.',
        )

    def handle(self, *args, **options):
        dry = options['dry_run']
        items = VocabularyItem.objects.select_related('category').all()

        counts = {1: 0, 2: 0, 3: 0}
        changes = 0
        to_update = []

        for item in items:
            new_diff = _difficulty(item.word_en)
            if new_diff != item.difficulty:
                changes += 1
                if not dry:
                    item.difficulty = new_diff
                    to_update.append(item)
                else:
                    self.stdout.write(
                        f'  {item.word_en:<22} {item.word_es:<22} '
                        f'{item.difficulty} -> {new_diff}'
                    )
            counts[new_diff] += 1

        if not dry and to_update:
            VocabularyItem.objects.bulk_update(to_update, ['difficulty'])

        mode = '[DRY-RUN] ' if dry else ''
        self.stdout.write(self.style.SUCCESS(
            f'\n{mode}Procesados: {items.count()} palabras | '
            f'Cambios: {changes} | '
            f'Fácil: {counts[1]} | Medio: {counts[2]} | Difícil: {counts[3]}'
        ))
