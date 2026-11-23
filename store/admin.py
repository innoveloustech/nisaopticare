from django.contrib import admin
from .models import Category, Customer, Product, Order,Profile, Brand, Review, StoreInfo
from .models import SubCategory, Gender, Banner, Blog, ProductImage, AddOnSettings
from django.contrib.auth.models import User



# Set custom branding
admin.site.site_header = "Nisa Opticare Admin Panel"
admin.site.site_title = "Nisa Opticare Admin"
admin.site.index_title = "Welcome to Nisa Opticare Administration"

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Gender)
# admin.site.register(Banner)
admin.site.register(Customer)
admin.site.register(Brand)
# admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Review)
admin.site.register(StoreInfo)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # You can upload 1 extra image at a time
    min_num = 0
    max_num = 10  # Optional limit

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_sale', 'quantity_in_stock', 'glass_type')
    list_filter = ('is_sale', 'glass_type', 'category')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]  # Attach additional images inline

admin.site.register(Product, ProductAdmin)


# Mix profile info and user info
class ProfileInline(admin.StackedInline):
	model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
	model = User
	field = ["username", "first_name", "last_name", "email"]
	inlines = [ProfileInline]

# Unregister the old way
admin.site.unregister(User)

# Re-Register the new way
admin.site.register(User, UserAdmin)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'created_at']
    list_filter = ['active']
    ordering = ['-created_at']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority', 'created_at')
    list_editable = ('is_active', 'priority')
    search_fields = ('title', 'keywords')

@admin.register(AddOnSettings)
class AddOnSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding more than 1 instance
        return not AddOnSettings.objects.exists()


