from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfesorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('institucion', models.CharField(blank=True, max_length=200)),
                ('codigo_clase', models.CharField(blank=True, max_length=10, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profesor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Salon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100)),
                ('grado', models.CharField(max_length=20, choices=[('1','1° Primaria'),('2','2° Primaria'),('3','3° Primaria'),('4','4° Primaria'),('5','5° Primaria')])),
                ('codigo_clase', models.CharField(blank=True, max_length=8, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('profesor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salones', to='accounts.profesorprofile')),
            ],
            options={'ordering': ['grado', 'nombre']},
        ),
        migrations.CreateModel(
            name='EstudianteProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('grado', models.CharField(blank=True, max_length=20)),
                ('numero_identidad', models.CharField(blank=True, max_length=20)),
                ('correo_padre', models.EmailField(blank=True)),
                ('puntos_totales', models.IntegerField(default=0)),
                ('nivel', models.IntegerField(default=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='estudiante_profile', to=settings.AUTH_USER_MODEL)),
                ('salon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estudiantes', to='accounts.salon')),
                ('profesor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estudiantes', to='accounts.profesorprofile')),
            ],
        ),
    ]
