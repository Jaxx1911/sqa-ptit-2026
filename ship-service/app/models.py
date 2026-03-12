from django.db import models


class Shipment(models.Model):
    order_id = models.IntegerField()
    shipping_method = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default="created")  # created, assigned, shipping, delivered
    shipper_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

