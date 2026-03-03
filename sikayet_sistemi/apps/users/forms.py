from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class CustomAuthenticationForm(AuthenticationForm):
    """Özelleştirilmiş giriş formu"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Kullanıcı adı'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Parola'
        })
    )


class CustomUserCreationForm(UserCreationForm):
    """Özelleştirilmiş kayıt formu - email ve telefon ile"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'E-posta adresiniz'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Telefon numaranız (opsiyonel)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Username alanını customize et
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Kullanıcı adı'
        })
        # Şifre alanlarını customize et
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Parola'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'Parola (tekrar)'
        })

    def clean_email(self):
        """Email'in benzersiz olduğunu kontrol et"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kayıtlı.')
        return email

    def save(self, commit=True):
        """Kullanıcıyı kaydet ve profil oluştur"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # UserProfile oluştur
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone': self.cleaned_data.get('phone', '')}
            )
        return user
