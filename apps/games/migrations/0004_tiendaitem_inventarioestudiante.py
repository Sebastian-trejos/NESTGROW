from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_artwork_paintingword'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TiendaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=200)),
                ('categoria', models.CharField(choices=[('mueble','🛋️ Mueble'),('decoracion','🖼️ Decoración'),('electronico','📺 Electrónico'),('planta','🌿 Planta/Natural'),('especial','✨ Especial')], default='decoracion', max_length=20)),
                ('costo_huesos', models.IntegerField(default=25)),
                ('icono', models.CharField(default='🛋️', max_length=10)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='tienda/')),
                ('posicion_x', models.IntegerField(default=0)),
                ('posicion_y', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('juego_desbloqueado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='desbloqueado_por', to='games.game')),
            ],
            options={'ordering': ['order', 'costo_huesos'], 'verbose_name': 'Item de Tienda'},
        ),
        migrations.CreateModel(
            name='InventarioEstudiante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('colocado_en_habitacion', models.BooleanField(default=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='propietarios', to='games.tiendaitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventario', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Inventario', 'unique_together': {('user', 'item')}},
        ),
    ]
