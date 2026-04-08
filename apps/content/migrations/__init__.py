from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nombre (Español)')),
                ('name_en', models.CharField(max_length=100, verbose_name='Nombre (Inglés)')),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(choices=[('🐾', 'Animales'), ('🎨', 'Colores'), ('🔢', 'Números'), ('🍎', 'Frutas'), ('🏠', 'Casa'), ('🏫', 'Escuela'), ('👗', 'Ropa'), ('🌦️', 'Clima'), ('👨\u200d👩\u200d👧', 'Familia'), ('🚗', 'Transporte'), ('🌿', 'Naturaleza'), ('🍔', 'Comida')], default='🐾', max_length=10)),
                ('color', models.CharField(default='#6C63FF', help_text='Color HEX para la tarjeta (ej: #FF6B6B)', max_length=7)),
                ('order', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/')),
            ],
            options={'verbose_name': 'Categoría', 'verbose_name_plural': 'Categorías', 'ordering': ['order', 'name']},
        ),
        migrations.CreateModel(
            name='VocabularyItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('word_es', models.CharField(max_length=100, verbose_name='Palabra en Español')),
                ('word_en', models.CharField(max_length=100, verbose_name='Word in English')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vocabulary/images/')),
                ('audio', models.FileField(blank=True, help_text='Archivo .mp3 con la pronunciación en inglés', null=True, upload_to='vocabulary/audio/')),
                ('hint', models.CharField(blank=True, max_length=200, verbose_name='Pista o contexto')),
                ('difficulty', models.IntegerField(choices=[(1, 'Fácil'), (2, 'Medio'), (3, 'Difícil')], default=1)),
                ('category', models.ForeignKey(on_delete=models.CASCADE, related_name='vocabulary', to='content.category')),
            ],
            options={'verbose_name': 'Vocabulario', 'verbose_name_plural': 'Vocabulario', 'ordering': ['word_en']},
        ),
    ]
