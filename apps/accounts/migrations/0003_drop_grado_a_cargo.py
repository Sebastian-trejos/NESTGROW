from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE accounts_profesorprofile DROP COLUMN grado_a_cargo;",
            reverse_sql="ALTER TABLE accounts_profesorprofile ADD COLUMN grado_a_cargo varchar(100) NOT NULL DEFAULT '';",
        ),
    ]
