from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import CustomUser
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    AdminLoginForm
)

# ============ User Views ============

@require_http_methods(["GET", "POST"])
def user_register(request):
    """Kullanıcı kayıt ekranı"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Kayıt başarılı! Lütfen giriş yapın.')
            return redirect('user_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Kullanıcı Kayıt'
    }
    return render(request, 'users/user_register.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    """Kullanıcı giriş ekranı"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.first_name}!')
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Kullanıcı Giriş'
    }
    return render(request, 'users/user_login.html', context)


@login_required(login_url='user_login')
def user_profile(request):
    """Kullanıcı profili"""
    context = {
        'page_title': 'Profil'
    }
    return render(request, 'users/user_profile.html', context)


# ============ Admin Views ============

@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Yönetici giriş ekranı"""
    if request.user.is_authenticated:
        if request.user.is_admin_user():
            return redirect('admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Yönetici paneline hoş geldiniz, {user.first_name}!')
            next_page = request.GET.get('next', 'admin_dashboard')
            return redirect(next_page)
    else:
        form = AdminLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Yönetici Giriş'
    }
    return render(request, 'users/admin_login.html', context)


def admin_dashboard(request):
    """Yönetici paneli"""
    if not request.user.is_authenticated or not request.user.is_admin_user():
        messages.error(request, 'Bu sayfaya erişim izniniz yok.')
        return redirect('admin_login')
    
    context = {
        'page_title': 'Yönetici Paneli',
        'total_users': CustomUser.objects.filter(user_type='user').count(),
        'total_admins': CustomUser.objects.filter(user_type='admin').count(),
    }
    return render(request, 'users/admin_dashboard.html', context)


def user_logout(request):
    """Çıkış"""
    logout(request)
    messages.success(request, 'Başarılı bir şekilde çıkış yaptınız.')
    return redirect('home')
