from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    """
    Kullanıcı kayıt formu
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Adınız'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Soyadınız'
        })
    )
    tc_id = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'TC Kimlik Numarası (11 hane)',
            'pattern': '[0-9]{11}'
        })
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': '+90 (5XX) XXX XX XX'
        })
    )
    address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Lütfen adresinizi yazınız...',
            'rows': 4
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'tc_id', 'email', 'phone', 'address', 'password1', 'password2')
    
    def clean_tc_id(self):
        tc_id = self.cleaned_data.get('tc_id')
        if not tc_id.isdigit():
            raise forms.ValidationError('TC Kimlik Numarası sadece rakamlardan oluşmalıdır.')
        if len(tc_id) != 11:
            raise forms.ValidationError('TC Kimlik Numarası 11 haneli olmalıdır.')
        if CustomUser.objects.filter(tc_id=tc_id).exists():
            raise forms.ValidationError('Bu TC Kimlik Numarası zaten kayıtlı.')
        return tc_id
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Basit telefon doğrulaması
        phone_digits = ''.join(filter(str.isdigit, phone))
        if len(phone_digits) < 10:
            raise forms.ValidationError('Geçersiz telefon numarası.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        # Email'den username generate et (@ işaretinden önceki kısmı kullan)
        email = cleaned_data.get('email')
        if email:
            username = email.split('@')[0]
            cleaned_data['username'] = username
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Şifre'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Şifre Onayı'
        })


class UserLoginForm(forms.Form):
    """
    Kullanıcı giriş formu (TC Kimlik Numarası + Şifre ile)
    """
    tc_id = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'TC Kimlik Numarası',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Şifre'
        })
    )
    
    def clean(self):
        tc_id = self.cleaned_data.get('tc_id')
        password = self.cleaned_data.get('password')
        
        if tc_id and password:
            try:
                user = CustomUser.objects.get(tc_id=tc_id)
                if not user.check_password(password):
                    raise forms.ValidationError('TC Kimlik Numarası veya şifre hatalı.')
                self.user_cache = user
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('TC Kimlik Numarası veya şifre hatalı.')
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)


class AdminLoginForm(forms.Form):
    """
    Yönetici giriş formu (TC Kimlik Numarası + Şifre ile)
    """
    tc_id = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'TC Kimlik Numarası',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition',
            'placeholder': 'Şifre'
        })
    )
    
    def clean(self):
        tc_id = self.cleaned_data.get('tc_id')
        password = self.cleaned_data.get('password')
        
        if tc_id and password:
            try:
                user = CustomUser.objects.get(tc_id=tc_id, user_type='admin')
                if not user.check_password(password):
                    raise forms.ValidationError('TC Kimlik Numarası veya şifre hatalı.')
                self.user_cache = user
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('TC Kimlik Numarası veya şifre hatalı.')
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)
