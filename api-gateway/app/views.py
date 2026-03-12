from django.shortcuts import render, redirect
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"


def home(request):
    return redirect("books")


def set_customer(request):
    if request.method == "POST":
        try:
            request.session["customer_id"] = int(request.POST.get("customer_id", 1))
        except (ValueError, TypeError):
            pass
    return redirect("books")


def book_list(request):
    customer_id = request.session.get("customer_id", 1)
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        books = r.json() if r.status_code == 200 else []
    except Exception:
        books = []
    return render(request, "books.html", {"books": books, "customer_id": customer_id})


def add_to_cart(request):
    if request.method == "POST":
        customer_id = request.session.get("customer_id", 1)
        book_id = request.POST.get("book_id")
        quantity = request.POST.get("quantity", 1)
        try:
            requests.post(
                f"{CART_SERVICE_URL}/cart-items/",
                json={"customer_id": customer_id, "book_id": int(book_id), "quantity": int(quantity)},
                timeout=5,
            )
        except Exception:
            pass
        return redirect("cart", customer_id=customer_id)
    return redirect("books")


def remove_cart_item(request, item_id):
    if request.method == "POST":
        customer_id = request.session.get("customer_id", 1)
        try:
            requests.delete(f"{CART_SERVICE_URL}/cart-items/{item_id}/", timeout=5)
        except Exception:
            pass
        return redirect("cart", customer_id=customer_id)
    return redirect("books")


def _enrich_cart_items(customer_id):
    """Fetch cart items and enrich with book data. Returns (enriched_items, total)."""
    try:
        r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/", timeout=5)
        items = r.json() if r.status_code == 200 else []
    except Exception:
        items = []

    try:
        br = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        books = {b["id"]: b for b in br.json()} if br.status_code == 200 else {}
    except Exception:
        books = {}

    enriched, total = [], 0.0
    for item in items:
        book = books.get(item["book_id"], {})
        subtotal = float(book.get("price", 0)) * item["quantity"]
        total += subtotal
        enriched.append({
            **item,
            "title": book.get("title", f"Book #{item['book_id']}"),
            "author": book.get("author", ""),
            "price": book.get("price", 0),
            "subtotal": round(subtotal, 2),
        })
    return enriched, round(total, 2)


def view_cart(request, customer_id):
    items, total = _enrich_cart_items(customer_id)
    return render(request, "cart.html", {"items": items, "customer_id": customer_id, "total": total})


def order_list(request):
    customer_id = request.session.get("customer_id", 1)
    try:
        r = requests.get(f"{ORDER_SERVICE_URL}/orders/", timeout=5)
        orders = r.json() if r.status_code == 200 else []
    except Exception:
        orders = []
    return render(request, "orders.html", {"orders": orders, "customer_id": customer_id})


def create_order(request, customer_id):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        shipping_method = request.POST.get("shipping_method")
        try:
            r = requests.post(
                f"{ORDER_SERVICE_URL}/orders/",
                json={"customer_id": customer_id, "payment_method": payment_method, "shipping_method": shipping_method},
                timeout=10,
            )
            if r.status_code == 201:
                order = r.json()
                return redirect("invoice", order_id=order["id"])
            error = r.json().get("error", "Order creation failed")
        except Exception:
            error = "Service unavailable. Please try again."
        items, total = _enrich_cart_items(customer_id)
        return render(request, "create_order.html", {"customer_id": customer_id, "items": items, "total": total, "error": error})

    items, total = _enrich_cart_items(customer_id)
    return render(request, "create_order.html", {"customer_id": customer_id, "items": items, "total": total})


def invoice(request, order_id):
    try:
        r = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}/", timeout=5)
        order = r.json() if r.status_code == 200 else None
    except Exception:
        order = None

    try:
        pr = requests.get(f"{PAY_SERVICE_URL}/payments/?order_id={order_id}", timeout=5)
        payments = pr.json() if pr.status_code == 200 else []
    except Exception:
        payments = []

    try:
        sr = requests.get(f"{SHIP_SERVICE_URL}/shipments/?order_id={order_id}", timeout=5)
        shipments = sr.json() if sr.status_code == 200 else []
    except Exception:
        shipments = []

    customer_id = request.session.get("customer_id", 1)
    return render(request, "invoice.html", {
        "order": order,
        "payment": payments[0] if payments else None,
        "shipment": shipments[0] if shipments else None,
        "order_id": order_id,
        "customer_id": customer_id,
    })

