from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import staff_required
from .forms import ProductForm
from .models import Category, Like, Product, Review

IPHONE_MODELS = [
    "iPhone 12", "iPhone 12 Pro", "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Pro",
]

SAMSUNG_MODELS = [
    "Samsung Galaxy S22", "Samsung Galaxy S23", "Samsung Galaxy S24", "Samsung Galaxy S24 Ultra",
    "Samsung Galaxy A05", "Samsung Galaxy A05s", "Samsung Galaxy A14", "Samsung Galaxy A15",
    "Samsung Galaxy A24", "Samsung Galaxy A25", "Samsung Galaxy A34", "Samsung Galaxy A35",
    "Samsung Galaxy A54", "Samsung Galaxy A55",
]


def _annotate_products(request, queryset):
    queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))
    if request.user.is_authenticated:
        like_subquery = Like.objects.filter(user=request.user, product=OuterRef('pk'))
        queryset = queryset.annotate(is_liked=Exists(like_subquery))
    return queryset


def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language in ('uz', 'ru'):
            request.session['language'] = language
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'shop:home'
    return redirect(next_url)


def home(request):
    featured_products = _annotate_products(
        request, Product.objects.filter(is_featured=True, in_stock=True)
    )[:8]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = _annotate_products(request, Product.objects.filter(in_stock=True))

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        _annotate_products(request, Product.objects.all()),
        slug=slug, in_stock=True,
    )
    reviews = product.reviews.select_related('user')
    related_products = list(_annotate_products(
        request,
        Product.objects.filter(category=product.category, in_stock=True).exclude(pk=product.pk)
    )[:6])
    if len(related_products) < 6:
        exclude_ids = [product.pk] + [p.pk for p in related_products]
        extra_needed = 6 - len(related_products)
        related_products += list(_annotate_products(
            request,
            Product.objects.filter(in_stock=True).exclude(pk__in=exclude_ids)
        )[:extra_needed])

    if 'samsung' in product.category.slug or 'samsung' in product.phone_model.lower():
        brand_models = SAMSUNG_MODELS
    else:
        brand_models = IPHONE_MODELS
    phone_models = list(brand_models)
    if product.phone_model not in phone_models:
        phone_models.append(product.phone_model)

    can_review = False
    already_reviewed = False
    if request.user.is_authenticated:
        from orders.models import OrderItem
        can_review = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sharh yozish uchun avval tizimga kiring.")
            return redirect('accounts:login')
        if not can_review:
            messages.error(request, "Sharh yozish uchun avval shu mahsulotni sotib olishingiz kerak.")
        elif already_reviewed:
            messages.error(request, "Siz bu mahsulotga allaqachon sharh qoldirgansiz.")
        else:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '').strip()
            if rating and comment:
                Review.objects.create(product=product, user=request.user, rating=int(rating), comment=comment)
                messages.success(request, "Sharhingiz uchun rahmat!")
                return redirect(product.get_absolute_url())
            messages.error(request, "Iltimos, baho va izoh kiriting.")

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'can_review': can_review,
        'already_reviewed': already_reviewed,
        'related_products': related_products,
        'phone_models': phone_models,
    })


@login_required
def submit_review(request, product_id):
    from orders.models import OrderItem

    product = get_object_or_404(Product, id=product_id)
    next_url = request.POST.get('next') or 'accounts:notifications'

    if request.method == 'POST':
        can_review = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not can_review:
            messages.error(request, "Sharh yozish uchun avval shu mahsulotni sotib olishingiz kerak.")
        elif already_reviewed:
            messages.error(request, "Siz bu mahsulotga allaqachon sharh qoldirgansiz.")
        elif rating and comment:
            Review.objects.create(product=product, user=request.user, rating=int(rating), comment=comment)
            messages.success(request, f"“{product.name}” uchun sharhingiz uchun rahmat!")
        else:
            messages.error(request, "Iltimos, baho va izoh kiriting.")

    return redirect(next_url)


@login_required
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if not created:
        like.delete()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'shop:home'
    return redirect(next_url)


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(in_stock=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(phone_model__icontains=query) | Q(description__icontains=query)
        )
    products = _annotate_products(request, products)
    categories = Category.objects.all()
    return render(request, 'shop/search_results.html', {
        'products': products,
        'query': query,
        'categories': categories,
    })


@login_required
def liked_products(request):
    products = _annotate_products(
        request, Product.objects.filter(likes__user=request.user)
    )
    return render(request, 'shop/liked_products.html', {'products': products})


@staff_required
def dashboard_products(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'shop/dashboard_products.html', {'products': products})


@staff_required
def dashboard_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangi mahsulot qo'shildi.")
            return redirect('shop:dashboard_products')
    else:
        form = ProductForm()
    return render(request, 'shop/dashboard_product_form.html', {'form': form, 'product': None})


@staff_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot yangilandi.")
            return redirect('shop:dashboard_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/dashboard_product_form.html', {'form': form, 'product': product})


@staff_required
def reply_to_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        reply_text = request.POST.get('admin_reply', '').strip()
        review.admin_reply = reply_text
        review.admin_reply_at = timezone.now() if reply_text else None
        review.save()

        if reply_text:
            from accounts.models import Notification
            Notification.objects.create(
                user=review.user,
                message=f"“{review.product.name}” mahsulotiga yozgan sharhingizga javob berildi.",
                link=review.product.get_absolute_url(),
            )
            messages.success(request, "Javobingiz yuborildi.")
        else:
            messages.success(request, "Javob o'chirildi.")

    next_url = request.POST.get('next') or review.product.get_absolute_url()
    return redirect(next_url)
