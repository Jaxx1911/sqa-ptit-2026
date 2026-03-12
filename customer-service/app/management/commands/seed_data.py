from django.core.management.base import BaseCommand
from app.models import Customer


class Command(BaseCommand):
    help = "Seed initial customers"

    def handle(self, *args, **options):
        if Customer.objects.exists():
            return

        customers = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"},
        ]

        for data in customers:
            Customer.objects.get_or_create(
                email=data["email"],
                defaults={"name": data["name"], "password": "pass"},
            )
