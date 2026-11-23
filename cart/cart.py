from store.models import Product, Profile

from decimal import Decimal
from store.models import AddOnSettings

import json

class Cart():
	def __init__(self, request):
		self.session = request.session
		# Get request
		self.request = request
		# Get the current session key if it exists
		cart = self.session.get('session_key')

		# If the user is new, no session key!  Create one!
		if 'session_key' not in request.session:
			cart = self.session['session_key'] = {}


		# Make sure cart is available on all pages of site
		self.cart = cart

	def db_add(self, product, quantity, **kwargs):
		product_id = str(product)
		product_qty = int(quantity)

		# If already exists, update quantity
		if product_id in self.cart:
			self.cart[product_id]['quantity'] = product_qty
		else:
			self.cart[product_id] = {
				'quantity': quantity,
				'cleaning_kit': kwargs.get('cleaning_kit', False),
				'prescription_type': kwargs.get('prescription_type', ''),
				'lens_type': kwargs.get('lens_type', ''),
				'right_sph': kwargs.get('right_sph', ''),
				'right_cyl': kwargs.get('right_cyl', ''),
				'right_axis': kwargs.get('right_axis', ''),
				'left_sph': kwargs.get('left_sph', ''),
				'left_cyl': kwargs.get('left_cyl', ''),
				'left_axis': kwargs.get('left_axis', ''),
				'prescription_text': kwargs.get('prescription_text', ''),
				'prescription_file': kwargs.get('prescription_file', ''),
			}

		self.session['session_key'] = self.cart
		self.session.modified = True

		# Save to DB if logged in
		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			carty = json.dumps(self.cart) 
			current_user.update(old_cart=carty)


	def add(self, product, quantity, **kwargs):
		product_id = str(product.id)

		# Build full cart item dict
		cart_item = {
			'quantity': quantity,
			'cleaning_kit': kwargs.get('cleaning_kit', False),
			'prescription_type': kwargs.get('prescription_type', ''),
			'lens_type': kwargs.get('lens_type', ''),
			'right_sph': kwargs.get('right_sph', ''),
			'right_cyl': kwargs.get('right_cyl', ''),
			'right_axis': kwargs.get('right_axis', ''),
			'left_sph': kwargs.get('left_sph', ''),
			'left_cyl': kwargs.get('left_cyl', ''),
			'left_axis': kwargs.get('left_axis', ''),
			'prescription_text': kwargs.get('prescription_text', ''),
			'prescription_file': kwargs.get('prescription_file', ''),
		}

		self.cart[product_id] = cart_item
		self.session['session_key'] = self.cart
		self.session.modified = True

		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# carty = str(self.cart).replace("'", '"')
			carty = json.dumps(self.cart) 
			current_user.update(old_cart=carty)



	def cart_total(self):
		product_ids = self.cart.keys()
		products = Product.objects.filter(id__in=product_ids)
		quantities = self.cart
		total = Decimal('0.00')

		# Load addon prices from DB
		addon_settings = AddOnSettings.get_solo()

		for product in products:
			key = str(product.id)
			item = quantities.get(key, {})
			qty = int(item.get('quantity', 1))
			line_total = Decimal('0.00')

			# Base price
			price = product.sale_price if product.is_sale else product.price
			line_total += price * qty

			# Add-on logic
			if item.get('cleaning_kit'):
				line_total += Decimal(addon_settings.extra_cleaning_kit_price) * qty

			# Non-prescription add-ons
			presc_type = item.get('prescription_type')
			if presc_type == 'frame_only':
				line_total += Decimal(addon_settings.frame_only_price) * qty
			elif presc_type == 'non_prescription':
				line_total += Decimal(addon_settings.non_prescription_blue_cut_price) * qty
			elif presc_type == 'sunglasses_only':
				line_total += Decimal(addon_settings.sunglasses_only_price) * qty
			elif presc_type == 'prescription_lens':
				lens_type = item.get('lens_type')
				if lens_type == 'blue_ray':
					line_total += Decimal(addon_settings.blue_ray_protection_price) * qty
				elif lens_type == 'cr_multicoated':
					line_total += Decimal(addon_settings.cr_multicoated_price) * qty
				elif lens_type == 'photochromatic':
					line_total += Decimal(addon_settings.photochromatic_lens_price) * qty
				elif lens_type == 'colored':
					line_total += Decimal(addon_settings.colored_lens_price) * qty

			total += line_total

		return total




	def __len__(self):
		return len(self.cart)

	def get_prods(self):
		# Get ids from cart
		product_ids = self.cart.keys()
		# Use ids to lookup products in database model
		products = Product.objects.filter(id__in=product_ids)

		# Return those looked up products
		return products

	def get_quants(self):
		quantities = self.cart
		return quantities

	def update(self, product, quantity):
		product_id = str(product)

		if product_id in self.cart:
			self.cart[product_id]['quantity'] = int(quantity)
			self.session['session_key'] = self.cart
			self.session.modified = True

			# Update in user profile
			if self.request.user.is_authenticated:
				current_user = Profile.objects.filter(user__id=self.request.user.id)
				carty = str(self.cart).replace("'", '"')
				current_user.update(old_cart=carty)

		return self.cart


	def delete(self, product):
		product_id = str(product)
		# Delete from dictionary/cart
		if product_id in self.cart:
			del self.cart[product_id]

		self.session.modified = True

		# Deal with logged in user
		if self.request.user.is_authenticated:
			# Get the current user profile
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# Convert {'3':1, '2':4} to {"3":1, "2":4}
			carty = str(self.cart)
			carty = carty.replace("\'", "\"")
			# Save carty to the Profile Model
			current_user.update(old_cart=str(carty))