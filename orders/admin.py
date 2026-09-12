from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone_number', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['full_name', 'phone_number', 'user__email']
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        status_changed = change and 'status' in form.changed_data
        super().save_model(request, obj, form, change)
        if status_changed:
            obj.notify_status_change()
