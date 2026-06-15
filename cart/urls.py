from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #<int:product_id> that is how Django knows exactly which product to put in the cart when a user clicks the button
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='cart_checkout'),
    path('my-orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
