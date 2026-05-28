from django.db import migrations, models


def eliminar_juegos_y_tienda(apps, schema_editor):
    Game = apps.get_model('games', 'Game')
    TiendaItem = apps.get_model('games', 'TiendaItem')
    Game.objects.filter(game_type__in=['quiz', 'ordenar_letras']).delete()
    TiendaItem.objects.filter(pk__in=[10, 11]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_memoriacard'),
    ]

    operations = [
        migrations.RunPython(eliminar_juegos_y_tienda, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('drag_and_drop', '🔗 Conectar imágenes con palabras'),
                    ('word_search', '🔍 Sopa de Letras'),
                    ('puzzle', '🧩 Rompecabezas'),
                    ('audio_matching', '🎵 Juego de Audio'),
                    ('painting', '🎨 Juego de Pintar'),
                    ('memoria', '🃏 Memoria'),
                    ('ahorcado', '🦴 Ahorcado de Milo'),
                    ('globos', '🎈 Globos'),
                    ('comparacion', '🖼️ Comparación'),
                ],
            ),
        ),
    ]
