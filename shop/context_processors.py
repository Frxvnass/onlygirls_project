from .models import Category


def categories(request):
    return {'categories': Category.objects.all()}


def language(request):
    return {'current_language': request.session.get('language', 'uz')}
