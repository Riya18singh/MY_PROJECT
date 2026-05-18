from django.urls import path
from . import views

urlpatterns = [
    # The Product List URL (e.g., yoursite.com/products/)
    path('products/', views.product_list, name='product_list'),

    # The Product Detail URL (e.g., yoursite.com/products/5/)
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
]
