from django.core.management.base import BaseCommand
from app.models import Cart, CartItem


class Command(BaseCommand):
    help = "Seed initial carts and cart items"

    def handle(self, *args, **options):
        if Cart.objects.exists():
            return

        # Assume seeded customers and books with IDs starting from 1
        cart, _ = Cart.objects.get_or_create(customer_id=1)

        CartItem.objects.get_or_create(cart=cart, book_id=1, defaults={"quantity": 1})
        CartItem.objects.get_or_create(cart=cart, book_id=2, defaults={"quantity": 2})

