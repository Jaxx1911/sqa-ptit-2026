from django.urls import path
from .views import CommentListCreate, RatingListCreate

urlpatterns = [
    path("comments/", CommentListCreate.as_view()),
    path("ratings/", RatingListCreate.as_view()),
]
