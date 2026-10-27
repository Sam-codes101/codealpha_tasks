from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import uuid

from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import CustomerSignUpForm, CustomerLoginForm, CheckoutForm


# -------------------------------------------------------------
# PRODUCT CATALOG & DETAILS
# -------------------------------------------------------------

def product_list_view(request):
    """Product catalog with category filter, search, and sorting."""
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'newest')

    products = Product.objects.all()
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
        'total_products': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail_view(request, slug):
    """Product detail page with specs, reviews, and related products."""
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


# -------------------------------------------------------------
# SHOPPING CART
# -------------------------------------------------------------

def cart_detail_view(request):
    """View shopping cart contents, order summary, and checkout CTA."""
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@require_POST
def cart_add_view(request, product_id):
    """Add product to cart via standard form or AJAX."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart.add(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"{product.name} added to cart!",
            'cart_count': len(cart),
            'cart_total': str(cart.get_total())
        })

    messages.success(request, f"Added {product.name} to your cart!")
    return redirect('cart_detail')


@require_POST
def cart_update_view(request, product_id):
    """Update item quantity in cart."""
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product_id=product_id, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'subtotal': str(cart.get_subtotal()),
            'shipping': str(cart.get_shipping_fee()),
            'total': str(cart.get_total())
        })

    return redirect('cart_detail')


@require_POST
def cart_remove_view(request, product_id):
    """Remove item from cart."""
    cart = Cart(request)
    cart.remove(product_id=product_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'subtotal': str(cart.get_subtotal()),
            'shipping': str(cart.get_shipping_fee()),
            'total': str(cart.get_total())
        })

    messages.info(request, "Item removed from cart.")
    return redirect('cart_detail')


# -------------------------------------------------------------
# CHECKOUT & ORDER PROCESSING
# -------------------------------------------------------------

def checkout_view(request):
    """Checkout page to place order."""
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty! Add some products before checking out.")
        return redirect('product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user

            order.order_number = f"NC-{uuid.uuid4().hex[:8].upper()}"
            order.subtotal = cart.get_subtotal()
            order.shipping_fee = cart.get_shipping_fee()
            order.total_price = cart.get_total()
            order.save()

            # Create OrderItems
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['price'],
                    quantity=item['quantity']
                )
                # Decrement stock
                product = item['product']
                if product.stock >= item['quantity']:
                    product.stock -= item['quantity']
                    product.save()

            # Clear cart
            cart.clear()
            messages.success(request, f"Order #{order.order_number} confirmed! Thank you for shopping with us.")
            return redirect('order_success', order_number=order.order_number)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})


def order_success_view(request, order_number):
    """Order confirmation receipt."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    """Customer account dashboard displaying past orders."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/order_history.html', {'orders': orders})


# -------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------

def signup_view(request):
    """Customer registration."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to NovaCart, {user.first_name or user.username}!")
            return redirect('product_list')
    else:
        form = CustomerSignUpForm()

    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    """Customer login."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'product_list'
            return redirect(next_url)
    else:
        form = CustomerLoginForm()

    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    """Customer logout."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('product_list')
