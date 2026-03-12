from django.urls import path
from .views import StaffListCreate, StaffLogin

urlpatterns = [
    path("staff/", StaffListCreate.as_view()),
    path("login/", StaffLogin.as_view()),
]
