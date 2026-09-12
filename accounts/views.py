from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Profile


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
            Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                photo=form.cleaned_data.get('photo'),
            )
            login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('shop:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


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
