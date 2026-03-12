from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Staff
from .serializers import StaffSerializer


class StaffListCreate(APIView):
    def get(self, request):
        qs = Staff.objects.all()
        role = request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        serializer = StaffSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class StaffLogin(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or password is None:
            return Response({"error": "email and password required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            staff = Staff.objects.get(email=email)
            if staff.password != password:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"id": staff.id, "name": staff.name, "email": staff.email, "role": staff.role})
        except Staff.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
