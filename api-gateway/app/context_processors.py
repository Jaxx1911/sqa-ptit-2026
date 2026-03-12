def gateway_session(request):
    """Add session auth info to template context."""
    user_role = request.session.get("user_role")
    staff_role = request.session.get("staff_role", "staff")  # staff | shipper
    return {
        "user_role": user_role,
        "user_name": request.session.get("user_name"),
        "user_id": request.session.get("user_id"),
        "customer_id": request.session.get("customer_id", 1),
        "staff_role": staff_role,
        "is_customer": user_role == "customer",
        "is_staff": user_role == "staff",
        "is_shipper": user_role == "staff" and staff_role == "shipper",
        "is_staff_books": user_role == "staff" and staff_role == "staff",
        "is_manager": user_role == "manager",
        "is_authenticated": bool(user_role),
    }
