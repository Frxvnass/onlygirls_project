from django.contrib import admin
from .models import Category, Like, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'phone_model', 'price', 'in_stock', 'is_featured', 'created_at']
    list_filter = ['category', 'in_stock', 'is_featured']
    list_editable = ['price', 'in_stock', 'is_featured']
    search_fields = ['name', 'phone_model']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__email', 'comment']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    search_fields = ['user__email', 'product__name']
