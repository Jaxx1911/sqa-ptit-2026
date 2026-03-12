from django.core.management.base import BaseCommand
from app.models import Comment, Rating


class Command(BaseCommand):
    help = "Seed initial comments and ratings (book_id 1,2,3 and customer_id 1,2)"

    def handle(self, *args, **options):
        if Comment.objects.exists() and Rating.objects.exists():
            return
        Comment.objects.get_or_create(
            book_id=1, customer_id=1, defaults={"text": "Great book on DDD!"}
        )
        Comment.objects.get_or_create(
            book_id=2, customer_id=1, defaults={"text": "Clean code practices."}
        )
        Comment.objects.get_or_create(
            book_id=1, customer_id=2, defaults={"text": "Very helpful for microservices."}
        )
        Rating.objects.get_or_create(
            book_id=1, customer_id=1, defaults={"score": 5}
        )
        Rating.objects.get_or_create(
            book_id=2, customer_id=1, defaults={"score": 4}
        )
        Rating.objects.get_or_create(
            book_id=1, customer_id=2, defaults={"score": 5}
        )
        Rating.objects.get_or_create(
            book_id=3, customer_id=2, defaults={"score": 4}
        )
