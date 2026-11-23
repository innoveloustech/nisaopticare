from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Profile, SubCategory, Gender, Brand, Banner, Blog, AddOnSettings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.core.paginator import Paginator

# from django.utils.http import urlunquote
from urllib.parse import unquote


from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q, Avg
import json
from cart.cart import Cart
from .models import Product, Review, Category, SubCategory, Gender
from .forms import ReviewForm

from django.db.models import Case, When, F, DecimalField, Value



def search(request):
    query = request.GET.get('search_key') or request.POST.get('searched')

    if query:
        search_terms = query.strip().split()
        products = Product.objects.all()

        for term in search_terms:
            products = products.filter(Q(name__icontains=term) | Q(description__icontains=term))

        if not products.exists():
            messages.info(request, "No products found for your search.")
            return render(request, "search.html", {'searched': [], 'query': query})
        else:
            return render(request, "search.html", {'searched': products, 'query': query})
    
    return render(request, "search.html", {})


def update_info(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access that page!")
        return redirect('home')

    # Get or create ShippingAddress for the user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your shipping info has been updated!")
            return redirect('home')
    else:
        form = UserInfoForm(instance=profile)

    return render(request, "update_info.html", {'form': form})



def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')
	

def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "User Has Been Updated!!")
			return redirect('home')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')


def category_summary(request):
	categories = Category.objects.all()
	subcategories = SubCategory.objects.all()
	genders = Gender.objects.all()
	
	return render(request, 'category_summary.html', {
        "categories": categories,
        "subcategories": subcategories,
        "genders": genders
    })



def category(request, foo):
    # Replace hyphens with spaces
    foo = foo.replace('-', ' ')

    # Try Category
    try:
        category = Category.objects.get(name__iexact=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {
            'products': products,
            'filter_type': 'Category',
            'filter_name': category.name
        })
    except Category.DoesNotExist:
        pass

    # Try SubCategory
    try:
        subcategory = SubCategory.objects.get(name__iexact=foo)
        products = Product.objects.filter(subcategory=subcategory)
        return render(request, 'category.html', {
            'products': products,
            'filter_type': 'Subcategory',
            'filter_name': subcategory.name
        })
    except SubCategory.DoesNotExist:
        pass

    # Try Gender
    try:
        gender = Gender.objects.get(name__iexact=foo)
        products = Product.objects.filter(gender=gender)
        return render(request, 'category.html', {
            'products': products,
            'filter_type': 'Gender',
            'filter_name': gender.name
        })
    except Gender.DoesNotExist:
        pass

    # If nothing matched
    messages.warning(request, "No category, subcategory, or gender matched.")
    return redirect('home')



def product(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']	
    addon_settings = AddOnSettings.get_solo()

    # Handle pre-fill data from GET parameters
    prefill_data = {
        'quantity': request.GET.get('quantity', 1),
        'cleaning_kit': request.GET.get('cleaning_kit') == 'True',
        'prescription_type': request.GET.get('prescription_type', ''),
        'lens_type': request.GET.get('lens_type', ''),
        'right_sph': request.GET.get('right_sph', ''),
        'right_cyl': request.GET.get('right_cyl', ''),
        'right_axis': request.GET.get('right_axis', ''),
        'left_sph': request.GET.get('left_sph', ''),
        'left_cyl': request.GET.get('left_cyl', ''),
        'left_axis': request.GET.get('left_axis', ''),
        'prescription_text': unquote(request.GET.get('prescription_text', '')),
		'prescription_file_url': request.GET.get('prescription_file_url', ''), 
    }

    # Review logic
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user if request.user.is_authenticated else None
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('product', pk=product.id)
    else:
        form = ReviewForm()

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating,
        'addon_settings': addon_settings,
        'prefill': prefill_data,
    })

def product_tryon(request, pk):
    product = get_object_or_404(Product, id=pk, enable_tryon=True)
    return render(request, "product_tryon.html", {"product": product})



def home(request):
	products = Product.objects.all()
	best_sellers = Product.objects.filter(is_best_seller=True)[:6]
	# reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:10]
	reviews = Review.objects.select_related('product', 'user') \
                            .filter(rating__gte=3) \
                            .order_by('-created_at')[:9]
	banners = Banner.objects.filter(active=True).order_by('-created_at')
	brands = Brand.objects.all()
	blogs = Blog.objects.filter(is_active=True)

	return render(request, 'home.html', {
		'products':products, 
		'best_sellers':best_sellers,
		'brands': brands,
		'blogs': blogs,
		'reviews': reviews,
		'banners': banners,
		})



def shop(request):
    products = Product.objects.all()
    # products = products.order_by('id')
    products = Product.objects.annotate(
        effective_price=Case(
            When(is_sale=True, then=F('sale_price')),
            default=F('price'),
            output_field=DecimalField()
        )
    )

    # Filters
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    gender = request.GET.get('gender')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category:
        products = products.filter(category_id=category)
    if subcategory:
        products = products.filter(subcategory_id=subcategory)
    if gender:
        products = products.filter(gender_id=gender)
    # if min_price:
    #     products = products.filter(price__gte=min_price)
    # if max_price:
    #     products = products.filter(price__lte=max_price)
    if min_price:
        products = products.filter(effective_price__gte=min_price)
    if max_price:
        products = products.filter(effective_price__lte=max_price)


    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        # products = products.order_by('price')
        products = products.order_by('effective_price')
    elif sort == 'price_desc':
        # products = products.order_by('-price')
        products = products.order_by('-effective_price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')

    if not sort:
        products = products.order_by('id')  # Fallback default ordering


    # Pagination
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'product_list.html', {
            'page_obj': page_obj
        })

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'genders': Gender.objects.all(),
        'filters': {
            'category': category,
            'subcategory': subcategory,
            'gender': gender,
            'min_price': min_price,
            'max_price': max_price,
        }
    }

    return render(request, 'shop.html', context)



def about(request):
	return render(request, 'about.html', {})	

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# Do some shopping cart stuff
			current_user = Profile.objects.get(user__id=request.user.id)
			# Get their saved cart from database
			saved_cart = current_user.old_cart
			# Convert database string to python dictionary
			if saved_cart:
				# Convert to dictionary using JSON
				converted_cart = json.loads(saved_cart)

				# try:
				# 	converted_cart = json.loads(saved_cart)
				# 	# proceed to load cart
				# except json.JSONDecodeError:
				# 	print("Corrupt cart, skipping load")
				# 	# optionally: clear it from DB
				# 	current_user.old_cart = "{}"
				# 	current_user.save()
				
				# Add the loaded cart dictionary to our session
				# Get the cart
				cart = Cart(request)

				# Loop thru the cart and add the items from the database
				# for key,value in converted_cart.items():
				# 	cart.db_add(product=key, quantity=value)

				for product_id, item_data in converted_cart.items():
					cart.db_add(
						product=product_id,
						quantity=item_data.get('quantity', 1),
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
						prescription_file=item_data.get('prescription_file', ''),
					)


			messages.success(request, ("You Have Been Logged In!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error, please try again..."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out...Thanks for stopping by..."))
	return redirect('home')



def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
			return redirect('update_info')
		else:
			messages.error(request, ("Whoops! There was a problem Registering. Please check the errors below..."))
			return render(request, 'register.html', {'form': form})
	else:
		return render(request, 'register.html', {'form': form})


def contact(request):
    return render(request, 'contact.html')


