from django.urls import path
from .views import (
    home, login_view, logout_view, register_view, set_customer, book_list, add_to_cart, remove_cart_item,
    view_cart, order_list, create_order, invoice,
    staff_book_list, staff_book_create, staff_book_edit, staff_book_delete,
    shipper_dashboard, shipper_claim,
    manager_users, manager_orders, manager_order_cancel, manager_ship_assign, manager_payments,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("set-customer/", set_customer, name="set_customer"),
    path("books/", book_list, name="books"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_cart_item, name="remove_cart_item"),
    path("cart/<int:customer_id>/", view_cart, name="cart"),
    path("orders/", order_list, name="orders"),
    path("orders/create/<int:customer_id>/", create_order, name="create_order"),
    path("orders/<int:order_id>/invoice/", invoice, name="invoice"),
    path("staff/books/", staff_book_list, name="staff_books"),
    path("staff/books/create/", staff_book_create, name="staff_book_create"),
    path("staff/books/<int:book_id>/edit/", staff_book_edit, name="staff_book_edit"),
    path("staff/books/<int:book_id>/delete/", staff_book_delete, name="staff_book_delete"),
    path("shipper/", shipper_dashboard, name="shipper_dashboard"),
    path("shipper/claim/<int:shipment_id>/", shipper_claim, name="shipper_claim"),
    path("manager/users/", manager_users, name="manager_users"),
    path("manager/orders/", manager_orders, name="manager_orders"),
    path("manager/orders/<int:order_id>/cancel/", manager_order_cancel, name="manager_order_cancel"),
    path("manager/orders/<int:order_id>/ship/", manager_ship_assign, name="manager_ship_assign"),
    path("manager/payments/", manager_payments, name="manager_payments"),
]