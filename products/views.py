from django.shortcuts import render,get_object_or_404
from .models import Product

def product_list(request):
    # Fetch all products from the database
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    # Fetch a specific product by its ID (pk)
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})
    