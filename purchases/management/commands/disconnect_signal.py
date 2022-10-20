# from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

# from django.db.models import signals
# from django.db.models.signals import post_save
# from purchases.signals import create_requisitioner


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = settings.AUTH_USER_MODEL
        print(User)
