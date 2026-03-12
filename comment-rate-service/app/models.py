from django.db import models


class Comment(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    score = models.IntegerField()  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)
