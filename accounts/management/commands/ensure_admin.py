import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "DJANGO_SUPERUSER_* o'zgaruvchilaridan admin hisobini yaratadi yoki yangilaydi."

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME/PASSWORD berilmagan, o\'tkazib yuborildi.')
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=username)
        user.email = os.environ.get('DJANGO_SUPERUSER_EMAIL', user.email)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin {'yaratildi' if created else 'yangilandi'}: {username}"
            )
        )
