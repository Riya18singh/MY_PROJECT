from django.shortcuts import render,get_object_or_404
from .models import Product, Category
import requests
from django.conf import settings
from decimal import Decimal

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
    product = get_object_or_404(Product, pk=pk)
    usd_price = None

    if request.GET.get('convert') == 'usd':
        api_url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/INR"

        try:
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                live_usd_rate = Decimal(str(data['conversion_rates']['USD']))
                usd_price = product.price * live_usd_rate
        except requests.exceptions.RequestException:
            pass

    return render(request, 'products/product_detail.html', {
        'product': product,
        'usd_price': usd_price
    })
