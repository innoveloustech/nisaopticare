from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from store.models import AddOnSettings

from store.models import AddOnSettings

def cart_summary(request):
    cart = Cart(request)
    products = cart.get_prods()
    quantities = cart.get_quants()  # dict of {product_id: item_data}
    addon_settings = AddOnSettings.get_solo()

    cart_items = []

    for product in products:
        prod_id = str(product.id)
        item_data = quantities.get(prod_id, {})

        quantity = item_data.get('quantity', 1)
        unit_price = product.sale_price if product.is_sale else product.price

        # Calculate addon total
        addon_total = 0
        addon_breakdown = []

        # Cleaning kit
        if item_data.get('cleaning_kit'):
            price = addon_settings.extra_cleaning_kit_price
            addon_total += price
            addon_breakdown.append({
                'name': 'Extra Cleaning Kit',
                'price': price
            })

        # Prescription type based addons
        prescription_type = item_data.get('prescription_type')
        lens_type = item_data.get('lens_type')

        if prescription_type == 'sunglasses_only':
            price = addon_settings.sunglasses_only_price
            addon_total += price
            addon_breakdown.append({'name': 'Sunglasses Only', 'price': price})
        elif prescription_type == 'frame_only':
            price = addon_settings.frame_only_price
            addon_total += price
            addon_breakdown.append({'name': 'Frame Only', 'price': price})
        elif prescription_type == 'non_prescription_blue_cut':
            price = addon_settings.non_prescription_blue_cut_price
            addon_total += price
            addon_breakdown.append({'name': 'Non Prescription Blue Cut', 'price': price})
        elif prescription_type == 'prescription_lens':
            # Lens type
            if lens_type == 'blue_ray':
                price = addon_settings.blue_ray_protection_price
                addon_breakdown.append({'name': 'Blue Ray Protection', 'price': price})
                addon_total += price
            elif lens_type == 'cr_multicoated':
                price = addon_settings.cr_multicoated_price
                addon_breakdown.append({'name': 'CR Multicoated', 'price': price})
                addon_total += price
            elif lens_type == 'photochromatic':
                price = addon_settings.photochromatic_lens_price
                addon_breakdown.append({'name': 'Photochromatic Lens', 'price': price})
                addon_total += price
            elif lens_type == 'colored':
                price = addon_settings.colored_lens_price
                addon_breakdown.append({'name': 'Colored Lens', 'price': price})
                addon_total += price

        subtotal = (unit_price + addon_total) * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': unit_price,
            'addon_total': addon_total,
            'addons': addon_breakdown,
            'subtotal': subtotal,

            # Existing fields
            'cleaning_kit': item_data.get('cleaning_kit'),
            'prescription_type': prescription_type,
            'lens_type': lens_type,
            'right_eye': {
                'sph': item_data.get('right_sph'),
                'cyl': item_data.get('right_cyl'),
                'axis': item_data.get('right_axis')
            },
            'left_eye': {
                'sph': item_data.get('left_sph'),
                'cyl': item_data.get('left_cyl'),
                'axis': item_data.get('left_axis')
            },
            'prescription_text': item_data.get('prescription_text'),
            'prescription_file': item_data.get('prescription_file'),
        })

    total_price = cart.cart_total()  # Your existing method is good

    

    return render(request, "cart_summary.html", {
        "cart_items": cart_items,
        "totals": total_price
    })




def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = str(request.POST.get('product_id'))  # Keep as string for session key
        product_qty = int(request.POST.get('product_qty') or 1)

        # Extra fields
        cleaning_kit = request.POST.get('cleaning_kit') == 'yes'
        prescription_type = request.POST.get('prescription_type')
        lens_type = request.POST.get('lens_type')

        right_sph = request.POST.get('right_sph')
        right_cyl = request.POST.get('right_cyl')
        right_axis = request.POST.get('right_axis')

        left_sph = request.POST.get('left_sph')
        left_cyl = request.POST.get('left_cyl')
        left_axis = request.POST.get('left_axis')

        prescription_text = request.POST.get('prescription_text')
        prescription_file = request.FILES.get('prescription_file')

        # Handle uploaded file
        file_path = None
        if prescription_file:
            path = f"prescriptions/{product_id}_{prescription_file.name}"
            file_path = default_storage.save(path, ContentFile(prescription_file.read()))

        # Get product instance
        product = get_object_or_404(Product, id=product_id)

        # Add to session cart
        cart.add(
            product=product,
            quantity=product_qty,
            cleaning_kit=cleaning_kit,
            prescription_type=prescription_type,
            lens_type=lens_type,
            right_sph=right_sph,
            right_cyl=right_cyl,
            right_axis=right_axis,
            left_sph=left_sph,
            left_cyl=left_cyl,
            left_axis=left_axis,
            prescription_text=prescription_text,
            prescription_file=file_path  # path saved in session
        )

        # Get updated cart quantity
        cart_quantity = cart.__len__()

        return JsonResponse({'qty': cart_quantity})


def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		# Call delete Function in Cart
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		#return redirect('cart_summary')
		messages.success(request, ("Item Deleted From Shopping Cart..."))
		return response


def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)

		response = JsonResponse({'qty':product_qty})
		#return redirect('cart_summary')
		messages.success(request, ("Your Cart Has Been Updated..."))
		return response

