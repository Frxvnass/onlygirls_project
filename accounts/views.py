import random
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Profile


def _send_verification_code(profile):
    profile.verification_code = f"{random.randint(0, 999999):06d}"
    profile.save()
    send_mail(
        subject="Emailingizni tasdiqlang — OnlyGirls",
        message=(
            f"Salom!\n\nOnlyGirls'da ro'yxatdan o'tish uchun quyidagi kodni "
            f"kiriting:\n\n{profile.verification_code}\n\n"
            f"Agar bu so'rovni siz yubormagan bo'lsangiz, xabarni e'tiborsiz qoldiring."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[profile.user.email],
        fail_silently=True,
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile = Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                photo=form.cleaned_data.get('photo'),
            )
            _send_verification_code(profile)
            login(request, user)
            messages.success(
                request,
                "Ro'yxatdan muvaffaqiyatli o'tdingiz! Gmail manzilingizga yuborilgan "
                "kodni kiriting."
            )
            return redirect('accounts:verify_email')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def verify_email(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.email_verified:
        return redirect('accounts:profile')

    if request.method == 'POST':
        if 'cancel' in request.POST:
            user = request.user
            logout(request)
            user.delete()
            messages.info(
                request,
                "Ro'yxatdan o'tish bekor qilindi. Gmail manzilingizni tekshirib qaytadan urinib ko'ring."
            )
            return redirect('accounts:register')
        elif 'resend' in request.POST:
            _send_verification_code(profile)
            messages.success(request, "Yangi kod gmailingizga yuborildi.")
        else:
            code = request.POST.get('code', '').strip()
            if code and code == profile.verification_code:
                profile.email_verified = True
                profile.verification_code = ''
                profile.save()
                messages.success(request, "Gmail manzilingiz tasdiqlandi!")
                return redirect('accounts:profile')
            messages.error(request, "Kod noto'g'ri. Qaytadan urinib ko'ring.")

    return render(request, 'accounts/verify_email.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next') or 'shop:home')
            form.add_error(None, "Email yoki parol noto'g'ri.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('shop:home')


@login_required
def profile(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_profile.phone_number = request.POST.get('phone_number', user_profile.phone_number)
        if request.FILES.get('photo'):
            user_profile.photo = request.FILES['photo']
        user_profile.save()

        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()

        messages.success(request, "Profilingiz yangilandi.")
        return redirect('accounts:profile')

    orders = request.user.orders.all()
    return render(request, 'accounts/profile.html', {'profile': user_profile, 'orders': orders})


@login_required
def notifications(request):
    from orders.models import Order
    from shop.models import Review

    qs = request.user.notifications.all()
    qs.filter(is_read=False).update(is_read=True)
    items = list(qs)

    for note in items:
        note.reviewable_products = []
        match = re.search(r'/success/(\d+)/', note.link)
        if not match:
            continue
        order = Order.objects.filter(
            id=int(match.group(1)), user=request.user, status=Order.STATUS_DELIVERED
        ).first()
        if not order:
            continue
        reviewed_ids = set(Review.objects.filter(
            user=request.user, product_id__in=[i.product_id for i in order.items.all()]
        ).values_list('product_id', flat=True))
        note.reviewable_products = [
            item.product for item in order.items.select_related('product').all()
            if item.product_id not in reviewed_ids
        ]

    return render(request, 'accounts/notifications.html', {'notifications': items})
