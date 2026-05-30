"""
Management command: python manage.py report_vocabulary_images

Reports which vocabulary items have a resolved image (uploaded or library)
and which ones still have no image at all.
"""
import sys

from django.core.management.base import BaseCommand
from apps.content.models import VocabularyItem


class Command(BaseCommand):
    help = 'Muestra que palabras de vocabulario tienen imagen y cuales no.'

    def handle(self, *args, **options):
        # Force UTF-8 output on Windows to avoid cp1252 errors
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        items = VocabularyItem.objects.select_related('category').order_by(
            'category__name', 'word_en'
        )

        con_imagen = []
        sin_imagen = []

        for item in items:
            url = item.display_image_url
            if url:
                source = '[subida]' if item.image else '[biblioteca]'
                con_imagen.append((item, url, source))
            else:
                sin_imagen.append(item)

        # ── Con imagen ────────────────────────────────────────────────────────
        self.stdout.write(
            self.style.SUCCESS(f'\nCON IMAGEN ({len(con_imagen)} palabras)\n{"="*50}')
        )
        current_cat = None
        for item, url, source in con_imagen:
            cat = item.category.name_en
            if cat != current_cat:
                self.stdout.write(f'\n  [{cat}]')
                current_cat = cat
            self.stdout.write(f'    + {item.word_en} / {item.word_es}  {source}')

        # ── Sin imagen ────────────────────────────────────────────────────────
        self.stdout.write(
            self.style.WARNING(f'\n\nSIN IMAGEN ({len(sin_imagen)} palabras)\n{"="*50}')
        )
        current_cat = None
        for item in sin_imagen:
            cat = item.category.name_en
            if cat != current_cat:
                self.stdout.write(f'\n  [{cat}]')
                current_cat = cat
            self.stdout.write(f'    - {item.word_en} / {item.word_es}')

        # ── Resumen ───────────────────────────────────────────────────────────
        total = len(con_imagen) + len(sin_imagen)
        pct = round(len(con_imagen) / total * 100) if total else 0
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nRESUMEN: {len(con_imagen)}/{total} palabras con imagen ({pct}%)\n'
            )
        )
        if sin_imagen:
            self.stdout.write(
                self.style.WARNING(
                    'TIP: Agrega imagenes a static/img/ con el nombre exacto '
                    'de la palabra (en ingles o espanol) para resolucion automatica.\n'
                )
            )
