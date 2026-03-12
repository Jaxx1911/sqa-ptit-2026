from django.urls import path
from .views import (
    home, set_customer, book_list, add_to_cart, remove_cart_item,
    view_cart, order_list, create_order, invoice,
)

urlpatterns = [
    path("", home, name="home"),
    path("set-customer/", set_customer, name="set_customer"),
    path("books/", book_list, name="books"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_cart_item, name="remove_cart_item"),
    path("cart/<int:customer_id>/", view_cart, name="cart"),
    path("orders/", order_list, name="orders"),
    path("orders/create/<int:customer_id>/", create_order, name="create_order"),
    path("orders/<int:order_id>/invoice/", invoice, name="invoice"),
]