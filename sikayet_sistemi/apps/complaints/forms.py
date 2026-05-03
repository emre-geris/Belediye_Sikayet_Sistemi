from django import forms
from .models import Complaint
from .districts import get_district_choices

class ComplaintForm(forms.ModelForm):
    # Override district field to be a ChoiceField
    district = forms.ChoiceField(
        label='İlçe',
        required=True,
        choices=get_district_choices(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
            'id': 'district-select'
        })
    )
    
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'city', 'district', 'address', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
                'placeholder': 'Şikayet başlığını giriniz...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
                'placeholder': 'Detaylı açıklama giriniz...',
                'rows': 5
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
                'placeholder': 'İl giriniz...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2',
                'placeholder': 'Tam adres giriniz...',
                'rows': 3
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty option at the beginning
        self.fields['district'].choices = [('', '-- İlçe Seçiniz --')] + get_district_choices()
        
        # Make latitude and longitude optional since they're auto-populated
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
