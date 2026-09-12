from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('set-language/', views.set_language, name='set_language'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('like/<int:product_id>/', views.toggle_like, name='toggle_like'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/reply/', views.reply_to_review, name='reply_to_review'),
    path('liked/', views.liked_products, name='liked_products'),
    path('search/', views.search, name='search'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/add/', views.dashboard_product_add, name='dashboard_product_add'),
    path('dashboard/products/<int:pk>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
]
