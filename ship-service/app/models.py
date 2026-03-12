from django.db import models


class Shipment(models.Model):
    order_id = models.IntegerField()
    shipping_method = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default="created")
    created_at = models.DateTimeField(auto_now_add=True)

