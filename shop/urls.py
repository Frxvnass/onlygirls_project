from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('like/<int:product_id>/', views.toggle_like, name='toggle_like'),
    path('liked/', views.liked_products, name='liked_products'),
    path('search/', views.search, name='search'),
]
