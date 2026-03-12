from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentListCreate(APIView):
    def get(self, request):
        qs = Shipment.objects.all().order_by("-created_at")
        order_id = request.query_params.get("order_id")
        if order_id:
            qs = qs.filter(order_id=order_id)
        return Response(ShipmentSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            shipment = serializer.save(status="created")
            return Response(ShipmentSerializer(shipment).data, status=201)
        return Response(serializer.errors, status=400)

