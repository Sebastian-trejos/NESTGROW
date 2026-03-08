from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, ProfesorProfile, EstudianteProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'profesor':
            ProfesorProfile.objects.create(user=instance)
        elif instance.role == 'estudiante':
            EstudianteProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'profesor':
        if hasattr(instance, 'profesor_profile'):
            instance.profesor_profile.save()
    elif instance.role == 'estudiante':
        if hasattr(instance, 'estudiante_profile'):
            instance.estudiante_profile.save()
