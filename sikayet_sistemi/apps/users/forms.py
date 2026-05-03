from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser

INPUT_CSS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--card)] text-[var(--text)]'
COUNTRY_CODE_CSS = 'px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--card)] text-[var(--text)] w-24'
TEXTAREA_CSS = INPUT_CSS + ' resize-none'


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': INPUT_CSS, 'placeholder': 'E-posta adresiniz'})
    )
    name_validator = RegexValidator(
        regex=r'^[A-Za-zÇÖÜĞİŞçöüğiş\s-]+$',
        message='Ad ve soyad alanına sadece harfler girilebilir.'
    )

    first_name = forms.CharField(
        max_length=150,
        validators=[name_validator],
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Adınız',
            'pattern': '[A-Za-zÇÖÜĞİŞçöüğiş\s-]+',
            'oninput': 'this.value = this.value.replace(/[^A-Za-zÇÖÜĞİŞçöüğiş\s-]/g, "")'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        validators=[name_validator],
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Soyadınız',
            'pattern': '[A-Za-zÇÖÜĞİŞçöüğiş\s-]+',
            'oninput': 'this.value = this.value.replace(/[^A-Za-zÇÖÜĞİŞçöüğiş\s-]/g, "")'
        })
    )
    tc_id = forms.CharField(
        max_length=11,
        min_length=11,
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS,
            'placeholder': '11 haneli TC Kimlik No',
            'inputmode': 'numeric',
            'pattern': '[0-9]{11}',
            'maxlength': '11',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        })
    )
    country_code = forms.ChoiceField(
        choices=(
            ('+90', '+90'),
            ('+1', '+1'),
            ('+7', '+7'),
            ('+20', '+20'),
            ('+27', '+27'),
            ('+30', '+30'),
            ('+31', '+31'),
            ('+32', '+32'),
            ('+33', '+33'),
            ('+34', '+34'),
            ('+36', '+36'),
            ('+39', '+39'),
            ('+44', '+44'),
            ('+46', '+46'),
            ('+49', '+49'),
            ('+61', '+61'),
            ('+62', '+62'),
            ('+81', '+81'),
            ('+86', '+86'),
            ('+91', '+91'),
        ),
        widget=forms.Select(attrs={'class': COUNTRY_CODE_CSS})
    )
    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Telefon numaranız',
            'type': 'tel',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'maxlength': '10',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        })
    )
    address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': TEXTAREA_CSS, 'placeholder': 'Adresiniz', 'rows': 3})
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'tc_id',
            'email',
            'address',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': INPUT_CSS, 'placeholder': 'Şifreniz'})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CSS, 'placeholder': 'Şifrenizi tekrar giriniz'})

    def clean_tc_id(self):
        tc_id = self.cleaned_data.get('tc_id')

        if not tc_id.isdigit():
            raise forms.ValidationError("TC sadece rakam olmalıdır.")

        if len(tc_id) != 11:
            raise forms.ValidationError("TC 11 haneli olmalıdır.")

        if CustomUser.objects.filter(tc_id=tc_id).exists():
            raise forms.ValidationError("Bu TC zaten kayıtlı.")

        return tc_id

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()

        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("Ad alanına sadece harf giriniz.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()

        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("Soyad alanına sadece harf giriniz.")

        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        if not phone_number or not phone_number.isdigit():
            raise forms.ValidationError("Telefon numarası sadece rakamlardan oluşmalıdır.")

        if len(phone_number) != 10:
            raise forms.ValidationError("Telefon numarası 10 haneli olmalıdır.")

        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        country_code = self.cleaned_data.get('country_code')
        phone_number = self.cleaned_data.get('phone_number')
        user.phone = f"{country_code}{phone_number}"

        # EMAIL'den username üret
        email = self.cleaned_data.get("email")
        username = email.split("@")[0]

        # Eğer aynı username varsa sonuna sayı ekle
        counter = 1
        base_username = username
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user.username = username

        if commit:
            user.save()

        return user


# ================= LOGIN =================


class UserLoginForm(forms.Form):
    tc_id = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'TC Kimlik Numaranız'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CSS, 'placeholder': 'Şifreniz'}))

    def clean(self):
        cleaned_data = super().clean()
        tc_id = cleaned_data.get("tc_id")
        password = cleaned_data.get("password")

        if tc_id and password:
            try:
                user = CustomUser.objects.get(tc_id=tc_id)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("TC veya şifre hatalı.")

            if not user.check_password(password):
                raise forms.ValidationError("TC veya şifre hatalı.")

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)


class AdminLoginForm(forms.Form):
    tc_id = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'TC Kimlik Numaranız'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CSS, 'placeholder': 'Şifreniz'}))

    def clean(self):
        cleaned_data = super().clean()
        tc_id = cleaned_data.get("tc_id")
        password = cleaned_data.get("password")

        if tc_id and password:
            try:
                user = CustomUser.objects.get(tc_id=tc_id, user_type__in=['admin', 'system_admin'])
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Çalışan bilgileri hatalı.")

            if not user.check_password(password):
                raise forms.ValidationError("Çalışan bilgileri hatalı.")

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)