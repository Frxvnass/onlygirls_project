from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone_number', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'phone_number', 'user__email']
    inlines = [OrderItemInline]
