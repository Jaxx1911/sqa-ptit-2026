from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment, Rating
from .serializers import CommentSerializer, RatingSerializer


class CommentListCreate(APIView):
    def get(self, request):
        qs = Comment.objects.all().order_by("-created_at")
        book_id = request.query_params.get("book_id")
        if book_id:
            qs = qs.filter(book_id=int(book_id))
        serializer = CommentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingListCreate(APIView):
    def get(self, request):
        qs = Rating.objects.all().order_by("-created_at")
        book_id = request.query_params.get("book_id")
        if book_id:
            qs = qs.filter(book_id=int(book_id))
        serializer = RatingSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            score = serializer.validated_data.get("score")
            if score is None or score < 1 or score > 5:
                return Response({"error": "score must be 1-5"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
