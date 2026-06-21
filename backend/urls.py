from django.contrib import admin
from django.urls import path, include
from cart import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('users/', include('users.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('my-orders/', views.order_history, name='order_history'),
]
