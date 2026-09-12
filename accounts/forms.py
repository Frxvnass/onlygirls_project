from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Gmail manzili")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni tasdiqlang")
    phone_number = forms.CharField(max_length=20, label="Telefon raqami")
    photo = forms.ImageField(required=False, label="Suratingiz")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Ism', 'last_name': 'Familiya'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Faqat @gmail.com manzili bilan ro'yxatdan o'tish mumkin.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu gmail manzili allaqachon ro'yxatdan o'tgan.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', "Parollar bir-biriga mos emas.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label="Gmail manzili")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")
