from django.db import migrations


def drop_grado_a_cargo(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM pragma_table_info('accounts_profesorprofile') WHERE name='grado_a_cargo'"
        )
        if cursor.fetchone():
            cursor.execute(
                "ALTER TABLE accounts_profesorprofile DROP COLUMN grado_a_cargo"
            )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.RunPython(drop_grado_a_cargo, migrations.RunPython.noop),
    ]
