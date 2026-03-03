from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# Create your views here.

def register_view(request):
    """Yeni kullanıcı kaydı"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Kayıt başarılı. Hoş geldiniz!')
            return redirect('home')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/auth.html', {
        'register_form': form,
        'login_form': CustomAuthenticationForm(),
        'register_mode': True
    })


def login_view(request):
    """Kullanıcı girişi"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Giriş başarılı.')
            return redirect('home')
        else:
            messages.error(request, 'Kullanıcı adı veya parola hatalı.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/auth.html', {
        'login_form': form,
        'register_form': CustomUserCreationForm(),
        'register_mode': False
    })


def logout_view(request):
    """Çıkış yapıp ana sayfaya yönlendir"""
    logout(request)
    return redirect('home')


class ForgotPasswordForm(forms.Form):
    """Şifremi unuttum formu - email veya telefon ile arama"""
    email_or_phone = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'placeholder': 'E-posta adresiniz veya telefon numaranızı giriniz...',
        }),
        label='E-posta veya Telefon'
    )


def forgot_password_view(request):
    """Şifremi unuttum sayfası"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            
            # E-posta ile kullanıcı ara
            try:
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                # E-postası yoksa mesaj göster (güvenlik nedeniyle spesifik olmayarak)
                messages.info(request, 'Eğer bir hesap varsa, şifre sıfırlama bağlantısı e-postanıza gönderilecektir.')
                return render(request, 'users/forgot_password.html', {'form': form})
            
            # Django'nun password reset işlemini başlat
            form_for_reset = PasswordResetForm({'email': user.email})
            if form_for_reset.is_valid():
                form_for_reset.save(
                    subject_template_name='users/password_reset_subject.txt',
                    email_template_name='users/password_reset_email.html',
                    from_email='noreply@sikayet.gov.tr',
                    request=request
                )
            messages.success(request, 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi. Lütfen e-postanızı kontrol edin.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'users/forgot_password.html', {'form': form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Şifre sıfırlama onayı sayfası"""
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
