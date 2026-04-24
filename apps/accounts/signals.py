from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, ProfesorProfile, EstudianteProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'profesor':
            ProfesorProfile.objects.get_or_create(
                user=instance,
                defaults={'institucion': ''}
            )
        elif instance.role == 'estudiante':
            EstudianteProfile.objects.get_or_create(user=instance)