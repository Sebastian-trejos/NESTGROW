from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
                ('name_en', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(max_length=10, default='🐾')),
                ('color', models.CharField(max_length=7, default='#6C63FF')),
                ('order', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/')),
            ],
            options={'ordering': ['order', 'name']},
        ),
        migrations.CreateModel(
            name='VocabularyItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('word_es', models.CharField(max_length=100)),
                ('word_en', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='vocabulary/images/')),
                ('audio', models.FileField(blank=True, null=True, upload_to='vocabulary/audio/')),
                ('hint', models.CharField(blank=True, max_length=200)),
                ('difficulty', models.IntegerField(choices=[(1, 'Fácil'), (2, 'Medio'), (3, 'Difícil')], default=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocabulary', to='content.category')),
            ],
            options={'ordering': ['word_en']},
        ),
    ]
