from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, Order
from .forms import ProductForm, ProductSearchForm, CartItemForm

def product_list(request):
    """Display all available products with search and filtering"""
    products = Product.objects.filter(status='available').select_related('category', 'seller')
    
    # Search and filtering
    search_form = ProductSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        condition = search_form.cleaned_data.get('condition')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        currency = search_form.cleaned_data.get('currency')
        
        if search:
            products = products.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        if category:
            products = products.filter(category=category)
        
        if condition:
            products = products.filter(condition=condition)
        
        if currency:
            products = products.filter(currency=currency)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    """Display detailed view of a single product"""
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(
        category=product.category,
        status='available'
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def create_product(request):
    """Create a new product listing"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product listing created successfully!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    return render(request, 'products/create_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    """Edit an existing product listing"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, pk):
    """Delete a product listing"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:my_listings')
    
    return render(request, 'products/delete_product.html', {'product': product})

@login_required
def my_listings(request):
    """Display user's own product listings"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'products/my_listings.html', context)

@login_required
def add_to_cart(request, pk):
    """Add a product to the user's cart"""
    product = get_object_or_404(Product, pk=pk, status='available')
    
    if product.seller == request.user:
        messages.error(request, 'You cannot add your own product to cart!')
        return redirect('products:product_detail', pk=pk)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Updated quantity for {product.title}')
    else:
        messages.success(request, f'{product.title} added to cart!')
    
    return redirect('products:cart')

@login_required
def cart(request):
    """Display user's cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'products/cart.html', context)

@login_required
def update_cart_item(request, pk):
    """Update quantity of a cart item"""
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cart updated!')
        else:
            messages.error(request, 'Invalid quantity!')
    
    return redirect('products:cart')

@login_required
def remove_from_cart(request, pk):
    """Remove an item from cart"""
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    messages.success(request, f'{product_title} removed from cart!')
    return redirect('products:cart')

@login_required
def checkout(request):
    """Process checkout and create orders"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('products:cart')
    
    # Create orders for each item
    orders_created = []
    for item in cart_items:
        order = Order.objects.create(
            buyer=request.user,
            seller=item.product.seller,
            product=item.product,
            quantity=item.quantity,
            total_price=item.product.price * item.quantity
        )
        orders_created.append(order)
        
        # Mark product as sold
        item.product.status = 'sold'
        item.product.save()
    
    # Clear the cart
    cart.items.all().delete()
    
    messages.success(request, f'Successfully placed {len(orders_created)} order(s)!')
    return redirect('products:orders')

@login_required
def orders(request):
    """Display user's purchase history"""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'products/orders.html', context)
