
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Complaint
from .forms import ComplaintForm
from apps.users.utils import create_status_notification
import json
from django.core.serializers.json import DjangoJSONEncoder

def home(request):
    """Ana sayfa - İstatistikleri göster"""
    total_complaints = Complaint.objects.count()
    new_complaints = Complaint.objects.filter(status='new').count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    urgent_complaints = Complaint.objects.filter(priority='urgent').count()

    # Son 5 şikayeti al
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]

    # En sık şikayet kategorileri
    categories = Complaint.objects.values('category').annotate(count=Count('category')).order_by('-count')[:5]

    all_complaints = Complaint.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).values('id', 'title', 'description', 'district', 'category', 'priority', 'latitude', 'longitude')

    context = {
        'total_complaints': total_complaints,
        'new_complaints': new_complaints,
        'resolved_complaints': resolved_complaints,
        'urgent_complaints': urgent_complaints,
        'recent_complaints': recent_complaints,
        'categories': categories,
        'complaints_json': json.dumps(list(all_complaints), cls=DjangoJSONEncoder),
    }
    return render(request, 'complaints/home.html', context)

class ComplaintListView(ListView):
    """Tüm şikayetleri listele"""
    model = Complaint
    template_name = 'complaints/complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def get_queryset(self):
        queryset = Complaint.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(district__icontains=search_query)
            )
        #filtreleme seçenekleri

        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority', '')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_category'] = self.request.GET.get('category', '')

        all_complaints = Complaint.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).values('id', 'title', 'description', 'district', 'category', 'priority', 'latitude', 'longitude')

        context['complaints_json'] = json.dumps(list(all_complaints), cls=DjangoJSONEncoder)
        return context

class ComplaintDetailView(DetailView):
    """Şikayet detaylarını göster"""
    model = Complaint
    template_name = 'complaints/complaint_detail.html'
    context_object_name = 'complaint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.is_admin_user():
            context['status_choices'] = Complaint.STATUS_CHOICES
            context['priority_choices'] = Complaint.PRIORITY_CHOICES
            context['category_choices'] = Complaint.CATEGORY_CHOICES
        return context

class ComplaintCreateView(LoginRequiredMixin, CreateView):
    """Yeni şikayet oluştur"""
    model = Complaint
    form_class = ComplaintForm
    template_name = 'complaints/complaint_form.html'
    success_url = reverse_lazy('complaint_list')

    def post(self, request, *args, **kwargs):
        # 1. Gelen form verilerini kopyalıyoruz
        data = request.POST.copy()
        
        # 2. ÖNEMLİ: Eğer 'priority' (öncelik) seçilmemişse manuel olarak 'medium' atıyoruz
        # Bu işlem formun 'is_valid' kontrolünden ÖNCE gerçekleştiği için hatayı engeller.
        if not data.get('priority'):
            data['priority'] = 'medium'
        
        # 3. Düzenlenmiş veriyi Django'nun orijinal POST verisiyle değiştiriyoruz
        request.POST = data
        # 4. Şimdi formu normal şekilde işleyebiliriz
        return super().post(request, *args, **kwargs)
    # Form doğrulama ve hata durumlarını loglamak için form_valid ve form_invalid metodlarını override ediyoruz

    def form_valid(self, form):
        # Kullanıcıyı bağla
        
        form.instance.user = self.request.user if self.request.user.is_authenticated else None
        print("\n>>> BAŞARI: Form doğrulandı ve kaydediliyor... <<<")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("\n!!! HATA: Form geçersiz! Detaylar: !!!")
        print(form.errors)
        return super().form_invalid(form)


@require_http_methods(["POST"])
def complaint_admin_update(request, pk):
    if not request.user.is_authenticated or not request.user.is_admin_user():
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('admin_login')

    complaint = get_object_or_404(Complaint, pk=pk)

    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    status = request.POST.get('status', '')
    priority = request.POST.get('priority', '')
    category = request.POST.get('category', '')

    valid_statuses = [c[0] for c in Complaint.STATUS_CHOICES]
    valid_priorities = [c[0] for c in Complaint.PRIORITY_CHOICES]
    valid_categories = [c[0] for c in Complaint.CATEGORY_CHOICES]
    old_status_display = complaint.get_status_display()

    if title:
        complaint.title = title
    if description:
        complaint.description = description
    if status in valid_statuses:
        complaint.status = status
    if priority in valid_priorities:
        complaint.priority = priority
    if category in valid_categories:
        complaint.category = category

    complaint.save()
    create_status_notification(complaint, old_status_display, complaint.get_status_display())
    messages.success(request, f'Şikayet #{pk} başarıyla güncellendi.')
    return redirect('complaint_detail', pk=pk)


@require_http_methods(["POST"])
def complaint_update_status(request, pk):
    if not request.user.is_authenticated or not request.user.is_admin_user():
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('admin_login')

    complaint = get_object_or_404(Complaint, pk=pk)
    new_status = request.POST.get('status')
    new_priority = request.POST.get('priority')
    updates = []
    old_status_display = complaint.get_status_display()

    valid_statuses = [choice[0] for choice in Complaint.STATUS_CHOICES]
    if new_status and new_status in valid_statuses:
        complaint.status = new_status
        updates.append(f'durum: {complaint.get_status_display()}')

    valid_priorities = [choice[0] for choice in Complaint.PRIORITY_CHOICES]
    if new_priority and new_priority in valid_priorities:
        complaint.priority = new_priority
        updates.append(f'öncelik: {complaint.get_priority_display()}')

    if updates:
        complaint.save()
        create_status_notification(complaint, old_status_display, complaint.get_status_display())
        messages.success(request, f'Şikayet #{pk} güncellendi ({", ".join(updates)}).')
    else:
        messages.error(request, 'Geçersiz değer.')

    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('complaint_detail', pk=pk)
    
