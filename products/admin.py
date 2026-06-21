from django.contrib import admin
#Register model here
from .models import Product, Category
admin.site.register(Category)
class ProductAdmin(admin.ModelAdmin):
    # We added 'category' to the list_display and list_filter!
    list_display = ['name', 'price', 'stock', 'category', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name']
    
admin.site.register(Product, ProductAdmin)


