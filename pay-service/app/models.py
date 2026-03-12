from django.db import models


class Payment(models.Model):
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)

