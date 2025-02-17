from django.contrib import admin
from .models import product, contact, Cart, Order, OrderItem


class OrderItemInline(admin.TabularInline):  
    """
    Inline admin class to show OrderItems inside the Order model.
    """
    model = OrderItem
    extra = 0  # Do not show extra blank rows
    fields = ('product', 'quantity', 'price')  # Fields to display
    readonly_fields = ('product', 'quantity', 'price')  # Make fields read-only to prevent editing here


class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Order model.
    """
    list_display = ('id', 'user', 'total_price', 'created_at')  # Fields to display in the Order list
    search_fields = ('user__username', 'id')  # Add search functionality
    list_filter = ('created_at',)  # Filter orders by creation date
    inlines = [OrderItemInline]  # Add inline for OrderItems


class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Cart model.
    """
    list_display = ('user', 'product', 'quantity', 'added_at')  # Fields to display in the list
    search_fields = ('user__username', 'product__product_name')  # Add search functionality


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price')  # Show these fields in admin panel
    list_filter = ('category',)  # Add filter by category
    search_fields = ('product_name', 'category')  # Enable search

admin.site.register(product, ProductAdmin)  # Register Product model with custom admin

# Register the models with their respective configurations
admin.site.register(Cart, CartAdmin)

admin.site.register(contact)
admin.site.register(Order, OrderAdmin)  # Register Order with OrderAdmin
admin.site.register(OrderItem)
