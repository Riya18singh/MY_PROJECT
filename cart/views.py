# Create your views here.
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.contrib import messages
from .models import Cart, CartItem
from orders.models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt

razor_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
    cart = Cart.objects.get(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

    # Razorpay uses paise
    razorpay_amount = int(total_price * 100)

    if request.method == 'POST':

        print("RAZORPAY KEY:", settings.RAZORPAY_KEY_ID)
        print("AMOUNT:", razorpay_amount)

        try:
            razorpay_order = razor_client.order.create({
                "amount": razorpay_amount,
                "currency": "INR",
                "payment_capture": 1
            })

            print("ORDER CREATED:", razorpay_order)

        except Exception as e:
            print("RAZORPAY ERROR:", e)
            raise

        # Create order in database
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='pending'
        )

        # Copy cart items into order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        context = {
            'order': order,
            'cart': cart,
            'total_price': total_price,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': razorpay_amount,
        }

        return render(request, 'cart/razorpay_checkout.html', context)

    return redirect('cart_detail')

@login_required(login_url='login')
def order_detail(request, order_id):
    # Security Check: Find the specific order, but ONLY if it belongs to this logged-in user!
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Send the data to a brand new receipt HTML page
    return render(request, 'products/order_detail.html', {'order': order})

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # 1. Grab the secure data Razorpay sends back
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        internal_order_id = request.POST.get('order_id')

        # 2. Verify the payment is 100% authentic
        try:
            razor_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            # 3. Find the order directly by its ID (bypassing the missing cookie)
            order = Order.objects.get(id=internal_order_id)
            order.status = 'Paid' 
            order.save()

            # 4. Find the cart using the Order's user, and empty it
            cart = Cart.objects.get(user=order.user)
            cart.items.all().delete()

            # 5. Show a success message and send them to their digital receipt
            messages.success(request, f"Payment successful! Order #{order.id} is confirmed.")
            return redirect('order_detail', order_id=order.id)

        # 6. If the signature is fake or fails, block the order
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('cart_detail')
            
    return redirect('cart_detail')      
