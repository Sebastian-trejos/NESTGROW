from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0013_add_pos_escala_inventario'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordSearchWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('word', models.CharField(max_length=100, help_text='Palabra a esconder en la sopa de letras')),
                ('order', models.PositiveIntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_search_words', to='games.game')),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]