from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

from shop.models import Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Kutilmoqda'),
        (STATUS_CONFIRMED, 'Tasdiqlandi'),
        (STATUS_SHIPPED, "Jo'natildi"),
        (STATUS_DELIVERED, 'Yetkazildi'),
        (STATUS_CANCELLED, 'Bekor qilindi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.full_name}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def notify_admins_new_order(self):
        from django.contrib.auth import get_user_model
        from accounts.models import Notification

        User = get_user_model()
        staff_users = User.objects.filter(is_staff=True)
        Notification.objects.bulk_create([
            Notification(
                user=staff_user,
                message=f"Yangi buyurtma #{self.id} tushdi — {self.full_name} ({self.get_total_cost()} so'm)",
                link=reverse('orders:dashboard_orders'),
            )
            for staff_user in staff_users
        ])

    def notify_status_change(self):
        from accounts.models import Notification

        Notification.objects.create(
            user=self.user,
            message=f"Buyurtma #{self.id} holati yangilandi: {self.get_status_display()}",
            link=reverse('orders:order_success', args=[self.id]),
        )
        if self.user.email:
            send_mail(
                subject=f"Buyurtma #{self.id} holati yangilandi — OnlyGirls",
                message=(
                    f"Salom, {self.full_name}!\n\n"
                    f"Sizning #{self.id}-raqamli buyurtmangiz holati yangilandi: "
                    f"{self.get_status_display()}.\n\n"
                    f"Rahmat, OnlyGirls jamoasi."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                fail_silently=True,
            )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    phone_model = models.CharField(max_length=100, blank=True)

    def get_cost(self):
        return self.price * self.quantity
