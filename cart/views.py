# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.contrib import messages
from .models import Cart, CartItem
from orders.models import Order, OrderItem

# The @login_required decorator forces users to log in before adding to cart
@login_required(login_url='login')
def add_to_cart(request, product_id):
    # Find the specific product the user clicked on
    product = get_object_or_404(Product, id=product_id)
    
    # Get the user's existing cart, or create a new one if it's their first time
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if this specific product is already in their cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # If they already had it in the cart, just add +1 to the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    #Send them back to the homepage for now
    return redirect('product_list')
@login_required(login_url='login')
def cart_detail(request):
    # Get the user's cart or create an empty one if they don't have one
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Calculate the total price of all items combined
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'total_price': total_price
    })
@login_required(login_url='login')
def update_cart(request, item_id):
    if request.method == 'POST':
        # 1. Safely find the item first
        item = get_object_or_404(CartItem, id=item_id)
        
        # 2. Security Check: Only let the user update it if they own it!
        if item.cart.user == request.user:
            new_quantity = int(request.POST.get('quantity', 1))
            
            if new_quantity > 0:
                item.quantity = new_quantity
                item.save()
                messages.success(request, f"Updated {item.product.name} quantity to {new_quantity}.")
            else:
                item.delete()
                messages.info(request, f"{item.product.name} was removed.")
                
    return redirect('cart_detail')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    # 1. Safely find the item first
    item = get_object_or_404(CartItem, id=item_id)
    
    # 2. Security Check: Only let the user delete it if they own it!
    if item.cart.user == request.user:
        item.delete()
        messages.warning(request, f"{item.product.name} was removed from your cart.")
        
    return redirect('cart_detail')

@login_required
def order_history(request):
    # Fetch all orders belonging to the logged-in user, newest first
    orders = Order.objects.filter(user=request.user).order_by('-id')
    
    return render(request, 'products/order_history.html', {'orders': orders})

@login_required(login_url='login')
def checkout(request):
    if request.method == 'POST':
        # 1. Find the user's current cart
        cart = Cart.objects.get(user=request.user)
        
        # 2. Calculate the total price
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        
        # 3. Create the permanent Order receipt
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )
        
        # 4. Copy the items from the Cart to the Order AND update inventory
        for cart_item in cart.items.all():
            product = cart_item.product
            quantity_bought = cart_item.quantity
            
            # Create the receipt item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity_bought,
                price=product.price
            )
            
            # quantity deducted
            product.stock -= quantity_bought
            product.save()
            
        # 5. Empty the shopping cart
        cart.items.all().delete()
        
        # 6. Send the user straight to their newly updated Order History!
        return redirect('order_history')
        
    # Fallback just in case they load the page incorrectly
    return redirect('cart_detail')
