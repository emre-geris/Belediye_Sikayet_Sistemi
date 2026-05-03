from apps.complaints.models import Complaint
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AdminLoginForm, UserLoginForm, UserRegistrationForm
from .models import CustomUser, Notification

# ============ User Views ============


@require_http_methods(["GET", "POST"])
def user_register(request):
    """Kullanıcı kayıt ekranı"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Kayıt başarılı! Lütfen giriş yapın.")
            return redirect("user_login")
    else:
        form = UserRegistrationForm()

    context = {"form": form, "page_title": "Kullanıcı Kayıt"}
    return render(request, "users/user_register.html", context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    """Kullanıcı giriş ekranı"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user_name = (
                user.first_name
                if user and user.first_name
                else user.username
                if user
                else "Kullanıcı"
            )
            messages.success(request, f"Hoş geldiniz, {user_name}!")
            next_page = request.GET.get("next", "home")
            return redirect(next_page)
    else:
        form = UserLoginForm()

    context = {"form": form, "page_title": "Kullanıcı Giriş"}
    return render(request, "users/user_login.html", context)


@login_required(login_url="user_login")
def user_profile(request):
    """Kullanıcı profili"""
    context = {"page_title": "Profil"}
    return render(request, "users/user_profile.html", context)


# ============ Admin Views ============


@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Yönetici giriş ekranı"""
    if request.user.is_authenticated:
        if request.user.is_admin_user():
            return redirect("admin_dashboard")
        else:
            return redirect("home")

    if request.method == "POST":
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user_name = (
                user.first_name
                if user and user.first_name
                else user.username
                if user
                else "Yönetici"
            )
            messages.success(request, f"Hoş geldiniz, {user_name}!")
            next_page = request.GET.get("next", "admin_dashboard")
            return redirect(next_page)
    else:
        form = AdminLoginForm()

    context = {"form": form, "page_title": "Yönetici Giriş"}
    return render(request, "users/admin_login.html", context)


def admin_dashboard(request):
    """Yönetici paneli"""
    if not request.user.is_authenticated or not request.user.is_admin_user():
        messages.error(request, "Bu sayfaya erişim izniniz yok.")
        return redirect("admin_login")

    complaints = Complaint.objects.order_by("-created_at")

    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    priority_filter = request.GET.get("priority", "")
    category_filter = request.GET.get("category", "")

    if search:
        complaints = complaints.filter(
            Q(title__icontains=search)
            | Q(district__icontains=search)
            | Q(description__icontains=search)
        )
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    context = {
        "page_title": "Yönetici Paneli",
        "total_users": CustomUser.objects.filter(user_type="user").count(),
        "total_workers": CustomUser.objects.filter(user_type="admin").count(),
        "total_complaints": Complaint.objects.count(),
        "new_complaints": Complaint.objects.filter(status="new").count(),
        "in_progress_complaints": Complaint.objects.filter(
            status="in_progress"
        ).count(),
        "resolved_complaints": Complaint.objects.filter(status="resolved").count(),
        "rejected_complaints": Complaint.objects.filter(status="rejected").count(),
        "complaints": complaints[:100],
        "status_choices": Complaint.STATUS_CHOICES,
        "priority_choices": Complaint.PRIORITY_CHOICES,
        "category_choices": Complaint.CATEGORY_CHOICES,
        "search": search,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "category_filter": category_filter,
    }
    return render(request, "users/admin_dashboard.html", context)


@login_required(login_url="user_login")
@require_http_methods(["POST"])
def mark_notifications_read(request):
    """Kullanıcının tüm bildirimlerini okundu işaretle."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "home"
    return redirect(next_url)


def user_logout(request):
    """Çıkış"""
    logout(request)
    messages.success(request, "Başarılı bir şekilde çıkış yaptınız.")
    return redirect("home")
