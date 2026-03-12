from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manager
from .serializers import ManagerSerializer


class ManagerList(APIView):
    def get(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)


class ManagerLogin(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or password is None:
            return Response({"error": "email and password required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            manager = Manager.objects.get(email=email)
            if manager.password != password:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"id": manager.id, "name": manager.name, "email": manager.email})
        except Manager.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
