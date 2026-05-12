from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_profesorprofile_codigo_clase'),
    ]

    operations = [
        migrations.RenameField(
            model_name='estudianteprofile',
            old_name='numero_identidad',
            new_name='numero_lista',
        ),
        migrations.AlterField(
            model_name='estudianteprofile',
            name='numero_lista',
            field=models.CharField(blank=True, max_length=10, verbose_name='N° de Lista'),
        ),
    ]
