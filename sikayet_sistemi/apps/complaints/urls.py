from django.urls import path
from . import views

urlpatterns = [
    path('', views.ComplaintListView.as_view(), name='complaint_list'),
    path('olustur/', views.ComplaintCreateView.as_view(), name='complaint_create'),
    path('<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('<int:pk>/durum/', views.complaint_update_status, name='complaint_update_status'),
]
