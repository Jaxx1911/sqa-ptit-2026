from django.core.management.base import BaseCommand
from app.models import Category


class Command(BaseCommand):
    help = "Seed initial categories"

    def handle(self, *args, **options):
        if Category.objects.exists():
            return
        Category.objects.get_or_create(slug="technical", defaults={"name": "Technical", "description": "Technical books"})
        Category.objects.get_or_create(slug="fiction", defaults={"name": "Fiction", "description": "Fiction books"})
        Category.objects.get_or_create(slug="business", defaults={"name": "Business", "description": "Business books"})
