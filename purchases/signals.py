from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Department, Requisitioner


@receiver(post_save, sender=User)
def create_requisitioner(sender, instance, created, **kwargs):
    if created:
        department = Department.objects.get(code='SEAS')
        Requisitioner.objects.create(user=instance,department=department)


@receiver(post_save, sender=User)
def save_requisitioner(sender, instance, **kwargs):
    instance.requisitioner.save()