from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Bu sahifaga faqat administratorlar kira oladi.")
            return redirect('shop:home')
        return view_func(request, *args, **kwargs)
    return wrapper
