from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer


class PaymentListCreate(APIView):
    def get(self, request):
        qs = Payment.objects.all().order_by("-created_at")
        order_id = request.query_params.get("order_id")
        if order_id:
            qs = qs.filter(order_id=order_id)
        return Response(PaymentSerializer(qs, many=True).data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(status="completed")
            return Response(PaymentSerializer(payment).data, status=201)
        return Response(serializer.errors, status=400)

