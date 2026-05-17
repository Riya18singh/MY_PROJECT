from django.shortcuts import render,get_object_or_404
from.models import products

# Create your views here.
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})

    