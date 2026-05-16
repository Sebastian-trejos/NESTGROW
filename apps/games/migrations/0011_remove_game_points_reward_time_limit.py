from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_add_puzzle_image_remove_atrapa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='points_reward',
        ),
        migrations.RemoveField(
            model_name='game',
            name='time_limit',
        ),
    ]
