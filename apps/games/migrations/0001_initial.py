from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=200)),
                ('title_en', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('game_type', models.CharField(choices=[('drag_and_drop', '🖱️ Arrastra y Suelta'), ('word_search', '🔍 Sopa de Letras'), ('puzzle', '🧩 Rompecabezas'), ('audio_matching', '🎵 Juego de Audio')], max_length=30)),
                ('difficulty', models.IntegerField(choices=[(1, '⭐ Fácil'), (2, '⭐⭐ Medio'), (3, '⭐⭐⭐ Difícil')], default=1)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='games/thumbnails/')),
                ('points_reward', models.IntegerField(default=5)),
                ('time_limit', models.IntegerField(default=120)),
                ('order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='content.category')),
            ],
            options={'verbose_name': 'Juego', 'verbose_name_plural': 'Juegos', 'ordering': ['order', 'title']},
        ),
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField(default=0)),
                ('max_score', models.IntegerField(default=0)),
                ('completed', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('time_spent', models.IntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_progress', to='games.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Progreso', 'verbose_name_plural': 'Progresos', 'unique_together': {('user', 'game')}},
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField()),
                ('max_score', models.IntegerField(default=0)),
                ('time_spent', models.IntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-score', 'time_spent']},
        ),
        migrations.CreateModel(
            name='Logro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=200)),
                ('icono', models.CharField(default='🏅', max_length=10)),
                ('categoria', models.CharField(choices=[('juegos', '🎮 Juegos'), ('puntaje', '⭐ Puntaje'), ('vocabulario', '📚 Vocabulario'), ('especial', '✨ Especial')], default='juegos', max_length=20)),
                ('condicion_valor', models.IntegerField(default=1)),
                ('color', models.CharField(default='#6C63FF', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Logro', 'verbose_name_plural': 'Logros'},
        ),
        migrations.CreateModel(
            name='LogroUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visto', models.BooleanField(default=False)),
                ('logro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='games.logro')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logros_obtenidos', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Logro de Usuario', 'unique_together': {('user', 'logro')}},
        ),
        migrations.CreateModel(
            name='HuesoTransaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tipo', models.CharField(choices=[('ganado', '🦴 Ganado'), ('gastado', '🛒 Gastado'), ('bonus', '🎁 Bonus')], default='ganado', max_length=10)),
                ('cantidad', models.IntegerField()),
                ('descripcion', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='huesos_transacciones', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
