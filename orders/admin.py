from django.contrib import admin
from .models import Order, OrderItem

# This allows to see the individual laptops inside the main Order screen
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  
    readonly_fields = ('product', 'quantity', 'price') 

# This customizes the main Order table in the dashboard
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]

# Officially register the models to the dashboard
admin.site.register(Order, OrderAdmin)
