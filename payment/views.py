from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime

# Import Some Paypal Stuff
from django.urls import reverse
# from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # unique user id for duplictate orders
from .models import BankDetail


def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=True, date_shipped=now)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def create_order_items(order, user, cart):
    cart_products = cart.get_prods()
    quantities = cart.get_quants()

    for product in cart_products:
        product_id = product.id
        price = product.sale_price if product.is_sale else product.price

        item_data = cart.cart.get(str(product_id), {})
        quantity_data = quantities.get(str(product_id), {})
        quantity = quantity_data.get('quantity', 1)  # ✅ FIXED

        OrderItem.objects.create(
            order=order,
            product=product,
            user=user if user.is_authenticated else None,
            quantity=quantity,
            price=price,

            cleaning_kit=item_data.get('cleaning_kit', False),
            prescription_type=item_data.get('prescription_type', ''),
            lens_type=item_data.get('lens_type', ''),
            right_sph=item_data.get('right_sph', ''),
            right_cyl=item_data.get('right_cyl', ''),
            right_axis=item_data.get('right_axis', ''),
            left_sph=item_data.get('left_sph', ''),
            left_cyl=item_data.get('left_cyl', ''),
            left_axis=item_data.get('left_axis', ''),
            prescription_text=item_data.get('prescription_text', ''),
            prescription_file=item_data.get('prescription_file', None),
        )

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = int(cart.cart_total())

    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(user=request.user)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            # No shipping address exists, try to get profile data for initial form data
            try:
                profile = Profile.objects.get(user=request.user)
                initial_data = {
                    'shipping_full_name': f"{request.user.first_name} {request.user.last_name}",
                    'shipping_email': request.user.email,
                    'shipping_address': getattr(profile, 'address', ''),
                    'shipping_city': getattr(profile, 'city', ''),
                    'shipping_province': getattr(profile, 'province', ''),
                    'shipping_zipcode': getattr(profile, 'zipcode', ''),
                    'shipping_country': getattr(profile, 'country', 'Pakistan'),
                }
            except Profile.DoesNotExist:
                initial_data = {
                    'shipping_full_name': f"{request.user.first_name} {request.user.last_name}",
                    'shipping_email': request.user.email,
                }

            shipping_form = ShippingForm(request.POST or None, initial=initial_data)
    else:
        shipping_form = ShippingForm(request.POST or None)

    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form,
    })


	
def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Convert POST data to dict and store in session
		my_shipping = request.POST.dict()
		request.session['my_shipping'] = my_shipping

		# Get the host
		host = request.get_host()

		# Get bank details
		bank_details = BankDetail.objects.first()

		# Pass the cleaned shipping dict to the template
		return render(request, "payment/billing_info.html", {
			"cart_products": cart_products,
			"quantities": quantities,
			"totals": totals,
			"shipping_form": my_shipping,  # ✅ This is now a dictionary!
			"bank_details": bank_details
		})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def process_order(request):
    if request.method == 'POST':
        cart = Cart(request)
        totals = cart.cart_total()

        my_shipping = request.session.get('my_shipping')
        if not my_shipping:
            messages.error(request, "Shipping information is missing. Please fill it before placing the order.")
            return redirect('checkout')  # or wherever you want to redirect to get shipping info

        # Safely access shipping info
        try:
            full_name = my_shipping['shipping_full_name']
            email = my_shipping['shipping_email']
            shipping_address = (
                f"{my_shipping['shipping_address']}\n"
                f"{my_shipping['shipping_city']}\n"
                f"{my_shipping['shipping_province']}\n"
                f"{my_shipping['shipping_zipcode']}\n"
                f"{my_shipping['shipping_country']}"
            )
        except KeyError as e:
            messages.error(request, f"Shipping information incomplete: missing {str(e)}.")
            return redirect('checkout')

        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        # Create order
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid
        )

        # Create order items
        create_order_items(order=order, user=request.user, cart=cart)

        # Clear cart session key (adjust key as per your cart implementation)
        if 'session_key' in request.session:
            del request.session['session_key']

        # Clear old cart info from profile if logged in
        if request.user.is_authenticated:
            Profile.objects.filter(user=request.user).update(old_cart="")

        messages.success(request, "Order Placed!")

        # return redirect('orders', pk=order.pk)
        if request.user.is_authenticated:
            return redirect('orders', pk=order.pk)
        else:
            return redirect('guest_order_summary', token=order.order_token)


    else: 
        messages.error(request, "Access Denied")
        return redirect('home')


def orders(request, pk):
    try:
        order = Order.objects.get(id=pk)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')

    # Allow superuser to view all orders
    if request.user.is_superuser:
        items = OrderItem.objects.filter(order=order)
    else:
        # Regular users can only view their own orders
        if request.user.is_authenticated and order.user == request.user:
            items = OrderItem.objects.filter(order=order)
        else:
            messages.error(request, "Access Denied")
            return redirect('home')

    return render(request, 'payment/orders.html', {"order": order, "items": items})


def guest_order_summary(request, token):
    try:
        order = Order.objects.get(order_token=token, user__isnull=True)
        items = OrderItem.objects.filter(order=order)
    except Order.DoesNotExist:
        messages.error(request, "Invalid or expired order link.")
        return redirect('home')

    return render(request, 'payment/orders.html', {
        "order": order,
        "items": items,
        "guest": True  # Optional: you can use this flag in template if needed
    })



def payment_success(request):
	return render(request, "payment/payment_success.html", {})


def payment_failed(request):
	return render(request, "payment/payment_failed.html", {})