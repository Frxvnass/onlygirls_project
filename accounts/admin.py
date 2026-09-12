from django.contrib import admin
from .models import Notification, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'email_verified']
    list_filter = ['email_verified']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone_number']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__email', 'message']
