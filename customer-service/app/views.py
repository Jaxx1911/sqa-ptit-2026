from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"


class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            try:
                requests.post(f"{CART_SERVICE_URL}/carts/", json={"customer_id": customer.id}, timeout=3)
            except Exception:
                pass
            return Response(serializer.data)
        return Response(serializer.errors)


class CustomerLogin(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or password is None:
            return Response({"error": "email and password required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = Customer.objects.get(email=email)
            if customer.password != password:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"id": customer.id, "name": customer.name, "email": customer.email})
        except Customer.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
