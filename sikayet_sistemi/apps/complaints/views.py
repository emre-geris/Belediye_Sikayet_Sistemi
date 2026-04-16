
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from .models import Complaint
from .forms import ComplaintForm
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

    context = {
        'total_complaints': total_complaints,
        'new_complaints': new_complaints,
        'resolved_complaints': resolved_complaints,
        'urgent_complaints': urgent_complaints,
        'recent_complaints': recent_complaints,
        'categories': categories,
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

class ComplaintCreateView(CreateView):
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
    