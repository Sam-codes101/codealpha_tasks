from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Order


class CustomerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create a password (min 6 chars)'}), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm your password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match!")
        return cleaned_data


class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))


class CheckoutForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('Credit / Debit Card', '💳 Credit / Debit Card'),
        ('UPI / Google Pay', '📱 UPI / Google Pay / NetBanking'),
        ('Cash on Delivery', '💵 Cash on Delivery (COD)'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect(attrs={'class': 'payment-radio'}))

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'postal_code', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10-digit Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Address, Apartment/Suite'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State / Province'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal PIN Code'}),
        }
