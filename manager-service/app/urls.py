from django.urls import path
from .views import ManagerList, ManagerLogin

urlpatterns = [
    path("managers/", ManagerList.as_view()),
    path("login/", ManagerLogin.as_view()),
]
