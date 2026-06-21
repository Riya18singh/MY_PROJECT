from django.urls import path
from . import views

urlpatterns = [
    # The Product List URL (Results in yoursite.com/products/)
    path('', views.product_list, name='product_list'),

    # The Product Detail URL (Results in yoursite.com/products/5/)
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('api/stats/', views.total_product_api, name='api stats'),
    path('api/on-sale/', views.on_sale_api, name='api-on-sale'),
]
