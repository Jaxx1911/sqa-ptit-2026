from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=64, default="staff")  # staff | shipper
    password = models.CharField(max_length=128, default="pass")
