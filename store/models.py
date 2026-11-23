from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone



# Create Customer Profile
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	date_modified = models.DateTimeField(auto_now=True)  # fix: should be auto_now=True, not User
	phone = models.CharField(max_length=20, blank=True)
	address = models.CharField(max_length=200, blank=True)  # renamed from address1 to address
	city = models.CharField(max_length=200, blank=True)
	province = models.CharField(max_length=200, blank=True)  # renamed from state to province
	zipcode = models.CharField(max_length=200, blank=True)
	country = models.CharField(max_length=200, blank=True)
	old_cart = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.user.username


# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
	if created:
		user_profile = Profile(user=instance)
		user_profile.save()

# Automate the profile thing
post_save.connect(create_profile, sender=User)


# Categories of Products
class Category(models.Model):
	
	name = models.CharField(max_length=100)
	image = models.ImageField(upload_to='category_images/', blank=True, null=True)

	def __str__(self):
		return self.name

	#@daverobb2011
	class Meta:
		verbose_name_plural = 'categories'


# Subcategories of Products
class SubCategory(models.Model):
	name = models.CharField(max_length=100)
	category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE, default=1)
	image = models.ImageField(upload_to='category_images/', blank=True, null=True)


	def __str__(self):
		return self.name

	#@daverobb2011
	class Meta:
		verbose_name_plural = 'subcategories'


class Gender(models.Model):
	name = models.CharField(max_length=100)
	image = models.ImageField(upload_to='category_images/', blank=True, null=True)

	def __str__(self):
		return self.name


# Customers
class Customer(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=10)
	email = models.EmailField(max_length=100)
	password = models.CharField(max_length=100)


	def __str__(self):
		return f'{self.first_name} {self.last_name}'
	

# Brands for collaboration
class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/')
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name
	



# All of our Products
class Product(models.Model):
	GLASS_TYPE_CHOICES = (
        ('sunglasses', 'Sunglasses'),
        ('eyeglasses', 'Eyeglasses'),
    )
	
	name = models.CharField(max_length=100)
	price = models.DecimalField(default=0, decimal_places=0, max_digits=8)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
	subcategory = models.ForeignKey(SubCategory, related_name='product', on_delete=models.CASCADE)
	gender = models.ForeignKey(Gender, related_name='product', on_delete=models.CASCADE, default=1)
	description = models.CharField(max_length=250, default='', blank=True, null=True)
	image = models.ImageField(upload_to='uploads/product/')
	# Add Sale Stuff
	is_sale = models.BooleanField(default=False)
	sale_price = models.DecimalField(default=0, decimal_places=0, max_digits=8)
	# Best Seller
	is_best_seller = models.BooleanField(default=False)
	# Brand collaboration
	brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)

	quantity_in_stock = models.PositiveIntegerField(default=0)
	glass_type = models.CharField(max_length=20, choices=GLASS_TYPE_CHOICES, default='sunglasses')
	
	# Virtual Try-On Feature
	enable_tryon = models.BooleanField(default=False)
	tryon_image = models.ImageField(upload_to='tryon/', blank=True, null=True)

	def __str__(self):
		return self.name
	
	def average_rating(self):
		reviews = self.reviews.all()
		if reviews.exists():
			return round(sum([r.rating for r in reviews]) / len(reviews), 1)
		return 0
	
# Additional images model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/product/extra/')

    def __str__(self):
        return f"Image for {self.product.name}"

# Customer Reviews
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.product.name} review by {self.user.username if self.user else "Guest"}'


# Customer Orders
class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	address = models.CharField(max_length=100, default='', blank=True)
	phone = models.CharField(max_length=20, default='', blank=True)
	date = models.DateField(default=datetime.datetime.today)
	status = models.BooleanField(default=False)

	def __str__(self):
		return self.product
	

# Banners for promotions
class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Banner {self.id}"

# Blog Posts
class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    keywords = models.CharField(max_length=255, help_text="Comma-separated search keywords")
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0, help_text="Lower value = higher priority")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return self.title
	
class AddOnSettings(models.Model):
    # Singleton pattern (only one row in DB)
    singleton_id = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)

    # Add-On Fields
    extra_cleaning_kit_price = models.PositiveIntegerField(default=150)
    sunglasses_only_price = models.PositiveIntegerField(default=0)
    frame_only_price = models.PositiveIntegerField(default=0)
    non_prescription_blue_cut_price = models.PositiveIntegerField(default=600)

    # Prescription Lens Types
    blue_ray_protection_price = models.PositiveIntegerField(default=1500)
    cr_multicoated_price = models.PositiveIntegerField(default=1100)
    photochromatic_lens_price = models.PositiveIntegerField(default=1700)
    colored_lens_price = models.PositiveIntegerField(default=2000)

    def __str__(self):
        return "Add-On Prices"

    def save(self, *args, **kwargs):
        self.singleton_id = 1  # ensure only one instance
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(singleton_id=1)[0]
	

class StoreInfo(models.Model):
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone_1 = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20, blank=True, null=True)

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)

    message = models.CharField(max_length=1023, blank=True, null=True)
    message_slide = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Store Info"
        verbose_name_plural = "Store Info"

    def __str__(self):
        return "Store Info"