from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

LOW_STOCK_THRESHOLD = 2


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    phone_model = models.CharField(max_length=100, help_text="Masalan: iPhone 15 Pro, Samsung S24")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Omborda qancha dona qolgani")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        previous_quantity = None
        if self.pk:
            previous_quantity = Product.objects.filter(pk=self.pk).values_list('stock_quantity', flat=True).first()
        super().save(*args, **kwargs)

        crossed_into_low_stock = self.stock_quantity <= LOW_STOCK_THRESHOLD and (
            previous_quantity is None or previous_quantity > LOW_STOCK_THRESHOLD
        )
        if crossed_into_low_stock:
            send_mail(
                subject=f"Omborda kam qoldi: {self.name} ({self.stock_quantity} dona)",
                message=(
                    f"\"{self.name}\" mahsulotidan omborda atigi {self.stock_quantity} dona qoldi.\n"
                    f"Iltimos, zaxirani to'ldiring."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ORDER_NOTIFICATION_EMAIL],
                fail_silently=True,
            )


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    admin_reply = models.TextField(blank=True)
    admin_reply_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
