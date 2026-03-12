from django.core.management.base import BaseCommand
from app.models import Manager


class Command(BaseCommand):
    help = "Seed initial managers"

    def handle(self, *args, **options):
        if Manager.objects.exists():
            return
        Manager.objects.get_or_create(email="manager@store.com", defaults={"name": "Store Manager", "password": "pass"})
        Manager.objects.get_or_create(email="admin@store.com", defaults={"name": "Admin Manager", "password": "pass"})
