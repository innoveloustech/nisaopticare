from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, BankDetail
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered


# ===========================
# OrderItem Admin
# ===========================
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'user',
        'quantity',
        'price',
        'cleaning_kit',
        'prescription_type',
        'lens_type',
        'right_sph',
        'right_cyl',
        'right_axis',
        'left_sph',
        'left_cyl',
        'left_axis',
        'prescription_text',
        'prescription_file',
    )
    readonly_fields = ['price', 'prescription_file']


# ===========================
# Order Inline (inside Order)
# ===========================
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0    
    readonly_fields = ['price', 'prescription_file']

# ===========================
# Order Admin
# ===========================
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = [
        "user", "full_name", "email", "shipping_address",
        "amount_paid", "date_ordered", "shipped", "date_shipped"
    ]
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'full_name', 'email', 'amount_paid', 'shipped', 'date_ordered', 'date_shipped')
    list_filter = ('shipped', 'date_ordered', 'date_shipped', 'user')
    search_fields = ('full_name', 'email', 'user__username')
    date_hierarchy = 'date_ordered'


# ===========================
# Register Models
# ===========================
admin.site.register(ShippingAddress)

try:
    admin.site.unregister(Order)
except NotRegistered:
    pass  # Already not registered, safe to continue


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)  

admin.site.register(BankDetail)

