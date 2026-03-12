from django.db import models


class Order(models.Model):
    customer_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, default="pending")
    payment_method = models.CharField(max_length=32)
    shipping_method = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

