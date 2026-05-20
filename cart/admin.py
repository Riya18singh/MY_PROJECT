from django.contrib import admin
from .models import Cart, CartItem

# 1. Define the inline layout for the items
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # This just stops Django from showing empty blank rows

# 2. Attach the inline layout to the main Cart admin
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

# 3. Register the Cart with the new layout (Notice we don't register CartItem alone anymore)
admin.site.register(Cart, CartAdmin)
