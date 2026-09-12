from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'phone_model', 'description', 'price',
            'image', 'image2', 'image3',
            'stock_quantity', 'in_stock', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
