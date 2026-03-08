from django.db import models


class TimeStampedModel(models.Model):
    """Abstract model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ActiveModel(models.Model):
    """Abstract model with active/inactive toggle."""
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        abstract = True
