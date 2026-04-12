from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
        ('content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(
                choices=[
                    ('drag_and_drop', '🖱️ Arrastra y Suelta'),
                    ('word_search', '🔍 Sopa de Letras'),
                    ('puzzle', '🧩 Rompecabezas'),
                    ('audio_matching', '🎵 Juego de Audio'),
                    ('painting', '🎨 Juego de Pintar'),
                ],
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='Artwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('canvas_data', models.TextField()),
                ('title', models.CharField(blank=True, max_length=200)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artworks', to='games.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artworks', to=settings.AUTH_USER_MODEL)),
                ('vocabulary_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='artworks', to='content.vocabularyitem')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='PaintingWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('word', models.CharField(max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='painting_words', to='games.game')),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]
