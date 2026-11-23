from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver 
from django.utils import timezone
import uuid


PROVINCE_CHOICES = [
	('', 'Select Province'),
	('Punjab', 'Punjab'),
	('Sindh', 'Sindh'),
	('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
	('Balochistan', 'Balochistan'),
	('Gilgit-Baltistan', 'Gilgit-Baltistan'),
	('Azad Jammu and Kashmir', 'Azad Jammu and Kashmir'),
]

class ShippingAddress(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	shipping_full_name = models.CharField(max_length=255)
	shipping_email = models.CharField(max_length=255)
	shipping_address = models.CharField(max_length=255)
	# shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
	shipping_city = models.CharField(max_length=255)
	shipping_province = models.CharField(max_length=255, null=True, blank=True, choices=PROVINCE_CHOICES)
	shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
	shipping_country = models.CharField(max_length=255, default='Pakistan')


	# Don't pluralize address
	class Meta:
		verbose_name_plural = "Shipping Address"

	def __str__(self):
		return f'Shipping Address - {str(self.id)}'

# Create a user Shipping Address by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
	if created:
		user_shipping = ShippingAddress(user=instance)
		user_shipping.save()

# Automate the profile thing
post_save.connect(create_shipping, sender=User)



# Create Order Model
class Order(models.Model):
	# Foreign Key
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	order_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
      
	full_name = models.CharField(max_length=250)
	email = models.EmailField(max_length=250)
	shipping_address = models.TextField(max_length=15000)
	amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
	date_ordered = models.DateTimeField(auto_now_add=True)	
	shipped = models.BooleanField(default=False)
	date_shipped = models.DateTimeField(blank=True, null=True)
	
	def __str__(self):
		return f'Order - {str(self.id)}'

# Auto Add shipping Date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
	# if instance.pk:
	# 	now = datetime.datetime.now()
	# 	obj = sender._default_manager.get(pk=instance.pk)
	# 	if instance.shipped and not obj.shipped:
	# 		instance.date_shipped = now
    if instance.pk:
        # Get previous state of the object
        obj = sender._default_manager.get(pk=instance.pk)

        # Check if shipped status changed from False to True
        if instance.shipped and not obj.shipped:
            # Set timezone to Pakistan Standard Time (UTC+5)
            instance.date_shipped = timezone.now()




# Create Order Items Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    cleaning_kit = models.BooleanField(default=False)
    prescription_type = models.CharField(max_length=100, blank=True, null=True)
    lens_type = models.CharField(max_length=100, blank=True, null=True)

    right_sph = models.CharField(max_length=20, blank=True, null=True)
    right_cyl = models.CharField(max_length=20, blank=True, null=True)
    right_axis = models.CharField(max_length=20, blank=True, null=True)

    left_sph = models.CharField(max_length=20, blank=True, null=True)
    left_cyl = models.CharField(max_length=20, blank=True, null=True)
    left_axis = models.CharField(max_length=20, blank=True, null=True)

    prescription_text = models.TextField(blank=True, null=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)

    def __str__(self):
        return f'Order Item - {str(self.id)}'

class BankDetail(models.Model):
    bank_name = models.CharField(max_length=100)
    account_title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50, blank=True)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_title}"