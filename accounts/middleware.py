from django.shortcuts import redirect
from django.urls import reverse

# Bu sahifalarga tasdiqlanmagan foydalanuvchi ham kira olishi kerak,
# aks holda kodni kiritish yoki chiqish imkoni bo'lmay qoladi.
EXEMPT_URL_NAMES = ('accounts:verify_email', 'accounts:logout')


class RequireEmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = None

    def __call__(self, request):
        if self.exempt_paths is None:
            self.exempt_paths = {reverse(name) for name in EXEMPT_URL_NAMES}

        user = request.user
        if (
            user.is_authenticated
            and not user.is_staff
            and request.path not in self.exempt_paths
            and not request.path.startswith('/admin/')
        ):
            profile = getattr(user, 'profile', None)
            if profile is not None and not profile.email_verified:
                return redirect('accounts:verify_email')

        return self.get_response(request)
