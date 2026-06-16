from django.shortcuts import render,get_object_or_404
from .models import Product, Category

def product_list(request):
    # 1. Grab all active products and all categories
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # 2. Check if the user clicked a specific Category button
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # 3. Check if the user typed something into the Search bar
    search_query = request.GET.get('q')
    if search_query:
        # __icontains means "find this word anywhere in the name, ignoring uppercase/lowercase"
        products = products.filter(name__icontains=search_query)

    # 4. Send the final filtered list to the HTML page
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
    })
def product_detail(request, pk):
    # Fetch a specific product by its ID (pk)
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})
    