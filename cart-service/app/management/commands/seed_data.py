from django.core.management.base import BaseCommand
from app.models import Cart, CartItem


class Command(BaseCommand):
    help = "Seed initial carts for customer_id 1,2,3 and sample cart items"

    def handle(self, *args, **options):
        for cid in [1, 2, 3]:
            Cart.objects.get_or_create(customer_id=cid)
        if CartItem.objects.exists():
            return
        cart1, _ = Cart.objects.get_or_create(customer_id=1)
        CartItem.objects.get_or_create(cart=cart1, book_id=1, defaults={"quantity": 1})
        CartItem.objects.get_or_create(cart=cart1, book_id=2, defaults={"quantity": 2})

