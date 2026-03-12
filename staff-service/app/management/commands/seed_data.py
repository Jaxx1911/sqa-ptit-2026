from django.core.management.base import BaseCommand
from app.models import Staff


class Command(BaseCommand):
    help = "Seed initial staff"

    def handle(self, *args, **options):
        if Staff.objects.exists():
            return
        Staff.objects.get_or_create(email="admin@store.com", defaults={"name": "Admin", "role": "staff", "password": "pass"})
        Staff.objects.get_or_create(email="staff@store.com", defaults={"name": "Staff User", "role": "staff", "password": "pass"})
        Staff.objects.get_or_create(email="shipper1@store.com", defaults={"name": "Shipper One", "role": "shipper", "password": "pass"})
        Staff.objects.get_or_create(email="shipper2@store.com", defaults={"name": "Shipper Two", "role": "shipper", "password": "pass"})
