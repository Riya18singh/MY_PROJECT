from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem

# Adjust this import based on exactly what app your Payment model is saved in!
# If it's in a 'payments' app, use: from payments.models import Payment
# If it's in 'orders', use: from .models import Payment
from payments.models import Payment 

@login_required(login_url='login')
def checkout(request):
    # 1. Safely grab the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    
    # 2. Block them from checking out if the cart is completely empty
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty. Add some items before checking out!")
        return redirect('cart_detail')

    if request.method == 'POST':
        # 3. Calculate the final total price one last time for security
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        # 4. Create the official Order snapshot
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='pending'
        )

        # 5. Move everything from the temporary Cart into permanent OrderItems
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # Taking the historical price snapshot!
            )

        # 6. Create the Payment record (Defaulting to Cash on Delivery for now)
        payment_method = request.POST.get('payment_method', 'cod')
        Payment.objects.create(
            user=request.user,
            order=order,
            method=payment_method,
            status='pending'
        )

        # 7. Empty the temporary cart so they can start shopping again
        cart.items.all().delete()

        # 8. Success! Send them back to the homepage
        messages.success(request, f"Order #{order.id} has been placed successfully!")
        return redirect('product_list')

    # If it is just a normal GET request, show them the checkout confirmation page
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    return render(request, 'orders/checkout.html', {'cart': cart, 'total_price': total_price})

