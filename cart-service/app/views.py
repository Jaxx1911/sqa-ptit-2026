from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"


class CartCreate(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=201 if created else 200)


class AddCartItem(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        book_id = request.data.get("book_id")
        quantity = int(request.data.get("quantity", 1))

        if not customer_id or not book_id:
            return Response({"error": "customer_id and book_id are required"}, status=400)

        # Get or create cart for customer
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)

        # Update quantity if item already in cart, otherwise create
        existing = CartItem.objects.filter(cart=cart, book_id=book_id).first()
        if existing:
            existing.quantity += quantity
            existing.save()
            return Response(CartItemSerializer(existing).data, status=200)

        item = CartItem.objects.create(cart=cart, book_id=book_id, quantity=quantity)
        return Response(CartItemSerializer(item).data, status=201)


class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            items = CartItem.objects.filter(cart=cart)
            return Response(CartItemSerializer(items, many=True).data)
        except Cart.DoesNotExist:
            return Response([])


class RemoveCartItem(APIView):
    def delete(self, request, item_id):
        try:
            CartItem.objects.get(id=item_id).delete()
            return Response({"message": "Item removed"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)


class ClearCart(APIView):
    def delete(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            pass
        return Response({"message": "Cart cleared"})
