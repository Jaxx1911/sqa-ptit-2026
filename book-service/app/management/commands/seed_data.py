from django.core.management.base import BaseCommand
from app.models import Book


class Command(BaseCommand):
    help = "Seed initial books"

    def handle(self, *args, **options):
        if Book.objects.exists():
            return

        books = [
            {"title": "Domain-Driven Design", "author": "Eric Evans", "price": 49.99, "stock": 10},
            {"title": "Clean Architecture", "author": "Robert C. Martin", "price": 39.99, "stock": 8},
            {"title": "Microservices Patterns", "author": "Chris Richardson", "price": 59.99, "stock": 5},
        ]

        for data in books:
            Book.objects.get_or_create(
                title=data["title"],
                author=data["author"],
                defaults={"price": data["price"], "stock": data["stock"]},
            )
