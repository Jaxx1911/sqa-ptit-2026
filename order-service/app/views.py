from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Order
from .serializers import OrderSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"


class OrderListCreate(APIView):
    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        customer_id = request.query_params.get("customer_id")
        if customer_id is not None:
            try:
                customer_id = int(customer_id)
                orders = orders.filter(customer_id=customer_id)
            except (ValueError, TypeError):
                pass
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        customer_id = request.data.get("customer_id")
        payment_method = request.data.get("payment_method")
        shipping_method = request.data.get("shipping_method")

        if not all([customer_id, payment_method, shipping_method]):
            return Response({"error": "Missing required fields"}, status=400)

        # Fetch cart items for customer
        cart_resp = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/", timeout=5)
        if cart_resp.status_code != 200:
            return Response({"error": "Failed to fetch cart"}, status=400)
        cart_items = cart_resp.json()

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=400)

        # Fetch books to compute total
        books_resp = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        if books_resp.status_code != 200:
            return Response({"error": "Failed to fetch books"}, status=400)
        books = {b["id"]: b for b in books_resp.json()}

        total = 0.0
        for item in cart_items:
            book_id = item["book_id"]
            qty = item["quantity"]
            if book_id not in books:
                return Response({"error": f"Book {book_id} not found"}, status=400)
            total += float(books[book_id]["price"]) * qty

        order = Order.objects.create(
            customer_id=customer_id,
            total_amount=round(total, 2),
            status="pending",
            payment_method=payment_method,
            shipping_method=shipping_method,
        )

        # Trigger payment
        pay_resp = requests.post(
            f"{PAY_SERVICE_URL}/payments/",
            json={"order_id": order.id, "amount": total, "method": payment_method},
            timeout=5,
        )
        if pay_resp.status_code != 201:
            order.status = "payment_failed"
            order.save()
            return Response({"error": "Payment failed"}, status=400)

        # Trigger shipping
        ship_resp = requests.post(
            f"{SHIP_SERVICE_URL}/shipments/",
            json={"order_id": order.id, "shipping_method": shipping_method},
            timeout=5,
        )
        if ship_resp.status_code != 201:
            order.status = "shipping_failed"
            order.save()
            return Response({"error": "Shipping failed"}, status=400)

        order.status = "completed"
        order.save()

        # Clear cart after successful order
        requests.delete(f"{CART_SERVICE_URL}/carts/{customer_id}/clear/", timeout=5)

        return Response(OrderSerializer(order).data, status=201)


class OrderDetail(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        status_val = request.data.get("status")
        if status_val is not None:
            order.status = status_val
            order.save()
        return Response(OrderSerializer(order).data)

