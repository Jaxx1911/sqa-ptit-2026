from django.core.management.base import BaseCommand
from app.models import Book


class Command(BaseCommand):
    help = "Seed initial books"

    def handle(self, *args, **options):
        if Book.objects.exists():
            return

        books = [
            {"title": "Domain-Driven Design", "author": "Eric Evans", "price": 49.99, "stock": 10, "image_url": "https://picsum.photos/seed/ddd1/300/400"},
            {"title": "Clean Architecture", "author": "Robert C. Martin", "price": 39.99, "stock": 8, "image_url": "https://picsum.photos/seed/clean1/300/400"},
            {"title": "Microservices Patterns", "author": "Chris Richardson", "price": 59.99, "stock": 5, "image_url": "https://picsum.photos/seed/ms1/300/400"},
            {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "price": 54.99, "stock": 12, "image_url": "https://picsum.photos/seed/ddia1/300/400"},
            {"title": "The Phoenix Project", "author": "Gene Kim", "price": 29.99, "stock": 15, "image_url": "https://picsum.photos/seed/phoenix1/300/400"},
            {"title": "Refactoring", "author": "Martin Fowler", "price": 44.99, "stock": 7, "image_url": "https://picsum.photos/seed/ref1/300/400"},
            {"title": "Building Microservices", "author": "Sam Newman", "price": 49.99, "stock": 6, "image_url": "https://picsum.photos/seed/bm1/300/400"},
            {"title": "Release It!", "author": "Michael T. Nygard", "price": 42.99, "stock": 4, "image_url": "https://picsum.photos/seed/rel1/300/400"},
        ]
        for data in books:
            Book.objects.get_or_create(
                title=data["title"],
                author=data["author"],
                defaults={"price": data["price"], "stock": data["stock"], "image_url": data.get("image_url", "")},
            )
