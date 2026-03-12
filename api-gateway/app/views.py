from django.shortcuts import render, redirect
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
CUSTOMER_SERVICE_URL = "http://customer-service:8000"
STAFF_SERVICE_URL = "http://staff-service:8000"
MANAGER_SERVICE_URL = "http://manager-service:8000"
CATALOG_SERVICE_URL = "http://catalog-service:8000"
COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"
RECOMMENDER_SERVICE_URL = "http://recommender-ai-service:8000"


def _require_role(role):
    """Decorator: redirect to login if session user_role is not role."""
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.session.get("user_role") != role:
                request.session["next_after_login"] = request.build_absolute_uri()
                return redirect("login")
            return view_func(request, *args, **kwargs)
        return wrap
    return decorator


def home(request):
    role = request.session.get("user_role")
    if role == "manager":
        return redirect("manager_orders")
    if role == "staff":
        staff_role = request.session.get("staff_role", "staff")
        if staff_role == "shipper":
            return redirect("shipper_dashboard")
        return redirect("staff_books")
    return redirect("books")


def login_view(request):
    if request.session.get("user_role"):
        return redirect("home")
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if not email:
            error = "Vui lòng nhập email."
        elif password is None:
            error = "Vui lòng nhập mật khẩu."
        else:
            # Xác định role từ DB: thử lần lượt manager → staff → customer
            role = None
            data = None
            for candidate, url in [
                ("manager", f"{MANAGER_SERVICE_URL}/login/"),
                ("staff", f"{STAFF_SERVICE_URL}/login/"),
                ("customer", f"{CUSTOMER_SERVICE_URL}/login/"),
            ]:
                try:
                    r = requests.post(url, json={"email": email, "password": password}, timeout=5)
                    if r.status_code == 200:
                        role = candidate
                        data = r.json()
                        break
                except Exception:
                    continue
            if role and data:
                request.session["user_role"] = role
                request.session["user_name"] = data.get("name", "")
                request.session["user_id"] = data.get("id")
                if role == "customer":
                    request.session["customer_id"] = data.get("id")
                if role == "staff":
                    request.session["staff_role"] = data.get("role", "staff")
                next_url = request.session.pop("next_after_login", None)
                if next_url:
                    return redirect(next_url)
                if role == "manager":
                    return redirect("manager_orders")
                if role == "staff":
                    sr = data.get("role", "staff")
                    if sr == "shipper":
                        return redirect("shipper_dashboard")
                    return redirect("staff_books")
                return redirect("books")
            error = "Email hoặc mật khẩu không đúng."
    return render(request, "login.html", {"error": error})


def logout_view(request):
    request.session.flush()
    return redirect("books")


def register_view(request):
    if request.session.get("user_role"):
        return redirect("home")
    error = None
    success = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if not name or not email or not password:
            error = "Please fill in name, email and password."
        else:
            try:
                r = requests.post(
                    f"{CUSTOMER_SERVICE_URL}/customers/",
                    json={"name": name, "email": email, "password": password},
                    timeout=5,
                )
                if r.status_code in (200, 201):
                    success = "Registration successful. Please sign in."
                else:
                    error = r.json().get("email", [r.text])[0] if isinstance(r.json().get("email"), list) else (r.json().get("error") or "Registration failed.")
            except Exception:
                error = "Service unavailable. Try again."
    return render(request, "register.html", {"error": error, "success": success})


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
    return render(request, "books.html", {"books": books})


def add_to_cart(request):
    if request.session.get("user_role") != "customer":
        request.session["next_after_login"] = request.build_absolute_uri(request.META.get("HTTP_REFERER", "/books/"))
        return redirect("login")
    if request.method == "POST":
        customer_id = request.session.get("customer_id")
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
    if request.session.get("user_role") != "customer":
        return redirect("login")
    if request.method == "POST":
        customer_id = request.session.get("customer_id")
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
            "image_url": book.get("image_url", ""),
            "subtotal": round(subtotal, 2),
        })
    return enriched, round(total, 2)


def view_cart(request, customer_id):
    if request.session.get("user_role") != "customer" or request.session.get("customer_id") != customer_id:
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    items, total = _enrich_cart_items(customer_id)
    return render(request, "cart.html", {"items": items, "total": total})


def order_list(request):
    if request.session.get("user_role") != "customer":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    customer_id = request.session.get("customer_id", 1)
    try:
        r = requests.get(f"{ORDER_SERVICE_URL}/orders/?customer_id={customer_id}", timeout=5)
        orders = r.json() if r.status_code == 200 else []
    except Exception:
        orders = []
    shipments_by_order = {}
    for order in orders:
        oid = order.get("id")
        if oid:
            try:
                sr = requests.get(f"{SHIP_SERVICE_URL}/shipments/?order_id={oid}", timeout=5)
                ship_list = sr.json() if sr.status_code == 200 else []
                shipments_by_order[oid] = ship_list[0] if ship_list else None
            except Exception:
                shipments_by_order[oid] = None
    for order in orders:
        order["shipment"] = shipments_by_order.get(order.get("id"))
    return render(request, "orders.html", {"orders": orders})


def create_order(request, customer_id):
    if request.session.get("user_role") != "customer" or request.session.get("customer_id") != customer_id:
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
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
    shipment = shipments[0] if shipments else None
    return render(request, "invoice.html", {
        "order": order,
        "payment": payments[0] if payments else None,
        "shipment": shipment,
        "order_id": order_id,
    })


# --- Staff: book management ---

def staff_book_list(request):
    if request.session.get("user_role") != "staff":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    if request.session.get("staff_role") == "shipper":
        return redirect("shipper_dashboard")
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        books = r.json() if r.status_code == 200 else []
    except Exception:
        books = []
    return render(request, "staff/books.html", {"books": books})


def staff_book_create(request):
    if request.session.get("user_role") != "staff" or request.session.get("staff_role") == "shipper":
        return redirect("login")
    if request.method == "POST":
        try:
            r = requests.post(
                f"{BOOK_SERVICE_URL}/books/",
                json={
                    "title": request.POST.get("title"),
                    "author": request.POST.get("author"),
                    "price": request.POST.get("price"),
                    "stock": request.POST.get("stock"),
                    "image_url": request.POST.get("image_url", ""),
                },
                timeout=5,
            )
            if r.status_code in (200, 201):
                return redirect("staff_books")
        except Exception:
            pass
    return redirect("staff_books")


def staff_book_edit(request, book_id):
    if request.session.get("user_role") != "staff" or request.session.get("staff_role") == "shipper":
        return redirect("login")
    if request.method == "POST":
        try:
            requests.patch(
                f"{BOOK_SERVICE_URL}/books/{book_id}/",
                json={
                    "title": request.POST.get("title"),
                    "author": request.POST.get("author"),
                    "price": request.POST.get("price"),
                    "stock": request.POST.get("stock"),
                    "image_url": request.POST.get("image_url", ""),
                },
                timeout=5,
            )
        except Exception:
            pass
        return redirect("staff_books")
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
        book = r.json() if r.status_code == 200 else None
    except Exception:
        book = None
    if not book:
        return redirect("staff_books")
    return render(request, "staff/book_edit.html", {"book": book})


def staff_book_delete(request, book_id):
    if request.session.get("user_role") != "staff" or request.session.get("staff_role") == "shipper":
        return redirect("login")
    if request.method == "POST":
        try:
            requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
        except Exception:
            pass
    return redirect("staff_books")


# --- Shipper: dashboard (unassigned + my shipments) ---

def shipper_dashboard(request):
    if request.session.get("user_role") != "staff" or request.session.get("staff_role") != "shipper":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    try:
        r = requests.get(f"{SHIP_SERVICE_URL}/shipments/", timeout=5)
        all_shipments = r.json() if r.status_code == 200 else []
    except Exception:
        all_shipments = []
    user_name = request.session.get("user_name", "")
    unassigned = [s for s in all_shipments if (s.get("status") == "created" and not (s.get("shipper_name") or "").strip())]
    my_shipments = [s for s in all_shipments if (s.get("shipper_name") or "").strip() == user_name]
    order_ids = set(s.get("order_id") for s in (unassigned + my_shipments) if s.get("order_id"))
    orders_by_id = {}
    for oid in order_ids:
        try:
            or_ = requests.get(f"{ORDER_SERVICE_URL}/orders/{oid}/", timeout=5)
            orders_by_id[oid] = or_.json() if or_.status_code == 200 else {}
        except Exception:
            orders_by_id[oid] = {}
    for s in unassigned + my_shipments:
        s["order_info"] = orders_by_id.get(s.get("order_id"), {})
    return render(request, "shipper/dashboard.html", {
        "unassigned": unassigned,
        "my_shipments": my_shipments,
    })


def shipper_claim(request, shipment_id):
    if request.session.get("user_role") != "staff" or request.session.get("staff_role") != "shipper":
        return redirect("login")
    if request.method == "POST":
        user_name = request.session.get("user_name", "")
        try:
            requests.patch(
                f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/",
                json={"shipper_name": user_name, "status": "assigned"},
                timeout=5,
            )
        except Exception:
            pass
    return redirect("shipper_dashboard")


# --- Manager: users ---

def manager_users(request):
    if request.session.get("user_role") != "manager":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    create_error = None
    create_success = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "") or "pass"
        role = request.POST.get("role", "customer").strip().lower()
        if not name or not email:
            create_error = "Vui lòng nhập tên và email."
        elif role == "customer":
            try:
                r = requests.post(
                    f"{CUSTOMER_SERVICE_URL}/customers/",
                    json={"name": name, "email": email, "password": password},
                    timeout=5,
                )
                if r.status_code in (200, 201):
                    create_success = "Đã tạo tài khoản khách hàng."
                else:
                    j = r.json() if r.content else {}
                    create_error = j.get("email", [j.get("error", "Lỗi tạo customer.")])[0] if isinstance(j.get("email"), list) else (j.get("error") or "Email có thể đã tồn tại.")
            except Exception:
                create_error = "Không kết nối được dịch vụ."
        elif role in ("staff", "shipper"):
            try:
                r = requests.post(
                    f"{STAFF_SERVICE_URL}/staff/",
                    json={"name": name, "email": email, "password": password, "role": role},
                    timeout=5,
                )
                if r.status_code in (200, 201):
                    create_success = f"Đã tạo tài khoản {role}."
                else:
                    j = r.json() if r.content else {}
                    create_error = j.get("email", [j.get("error", "Lỗi tạo staff.")])[0] if isinstance(j.get("email"), list) else (j.get("error") or "Email có thể đã tồn tại.")
            except Exception:
                create_error = "Không kết nối được dịch vụ."
        else:
            create_error = "Chọn role: Customer, Staff hoặc Shipper."
    try:
        cr = requests.get(f"{CUSTOMER_SERVICE_URL}/customers/", timeout=5)
        customers = cr.json() if cr.status_code == 200 else []
    except Exception:
        customers = []
    try:
        sr = requests.get(f"{STAFF_SERVICE_URL}/staff/", timeout=5)
        staff_list = sr.json() if sr.status_code == 200 else []
    except Exception:
        staff_list = []
    return render(request, "manager/users.html", {
        "customers": customers,
        "staff_list": staff_list,
        "create_error": create_error,
        "create_success": create_success,
    })


# --- Manager: orders (cancel, assign shipper) ---

def manager_orders(request):
    if request.session.get("user_role") != "manager":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    try:
        r = requests.get(f"{ORDER_SERVICE_URL}/orders/", timeout=5)
        orders = r.json() if r.status_code == 200 else []
    except Exception:
        orders = []
    shipments_by_order = {}
    for order in orders:
        oid = order.get("id")
        if oid:
            try:
                sr = requests.get(f"{SHIP_SERVICE_URL}/shipments/?order_id={oid}", timeout=5)
                ship_list = sr.json() if sr.status_code == 200 else []
                shipments_by_order[oid] = ship_list[0] if ship_list else None
            except Exception:
                shipments_by_order[oid] = None
    for order in orders:
        order["shipment"] = shipments_by_order.get(order.get("id"))
    try:
        sr = requests.get(f"{STAFF_SERVICE_URL}/staff/?role=shipper", timeout=5)
        shippers = sr.json() if sr.status_code == 200 else []
    except Exception:
        shippers = []
    return render(request, "manager/orders.html", {"orders": orders, "shippers": shippers})


def manager_order_cancel(request, order_id):
    if request.session.get("user_role") != "manager":
        return redirect("login")
    if request.method == "POST":
        try:
            requests.patch(
                f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                json={"status": "cancelled"},
                timeout=5,
            )
        except Exception:
            pass
    return redirect("manager_orders")


def manager_ship_assign(request, order_id):
    if request.session.get("user_role") != "manager":
        return redirect("login")
    if request.method == "POST":
        shipper_name = request.POST.get("shipper_name", "").strip()
        status_val = request.POST.get("status", "assigned")
        shipment_id = request.POST.get("shipment_id")
        if shipment_id and shipper_name:
            try:
                requests.patch(
                    f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/",
                    json={"shipper_name": shipper_name, "status": status_val},
                    timeout=5,
                )
            except Exception:
                pass
        elif shipment_id:
            try:
                requests.patch(
                    f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/",
                    json={"status": status_val},
                    timeout=5,
                )
            except Exception:
                pass
    return redirect("manager_orders")


# --- Manager: payment history ---

def manager_payments(request):
    if request.session.get("user_role") != "manager":
        request.session["next_after_login"] = request.build_absolute_uri()
        return redirect("login")
    try:
        r = requests.get(f"{PAY_SERVICE_URL}/payments/", timeout=5)
        payments = r.json() if r.status_code == 200 else []
    except Exception:
        payments = []
    return render(request, "manager/payments.html", {"payments": payments})

