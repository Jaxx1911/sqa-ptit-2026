from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import os

COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000")
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


class RecommendationList(APIView):
    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        try:
            r = requests.get(f"{COMMENT_RATE_SERVICE_URL}/ratings/", timeout=5)
            ratings = r.json() if r.status_code == 200 else []
        except Exception:
            ratings = []
        # Top rated books: aggregate by book_id (avg score), sort desc, return book_ids
        from collections import defaultdict
        book_scores = defaultdict(list)
        for item in ratings:
            book_scores[item["book_id"]].append(item["score"])
        book_avg = [(bid, sum(s) / len(s)) for bid, s in book_scores.items()]
        book_avg.sort(key=lambda x: -x[1])
        book_ids = [x[0] for x in book_avg[:10]]
        if not book_ids:
            # Fallback: get all books from book-service and return first few ids
            try:
                br = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
                books = br.json() if br.status_code == 200 else []
                book_ids = [b["id"] for b in books[:5]]
            except Exception:
                pass
        return Response({"book_ids": book_ids})
