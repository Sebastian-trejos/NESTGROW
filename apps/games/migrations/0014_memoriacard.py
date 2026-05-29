from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0013_wordsearchword'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemoriaCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('label_es', models.CharField(max_length=100, help_text='Texto en español de la tarjeta')),
                ('label_en', models.CharField(max_length=100, blank=True, help_text='Texto en inglés (opcional)')),
                ('image', models.ImageField(upload_to='games/memoria/', null=True, blank=True, help_text='Imagen de la tarjeta (opcional)')),
                ('order', models.PositiveIntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memoria_cards', to='games.game')),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]