from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    tc_id = forms.CharField(max_length=11)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(max_length=500)

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'tc_id',
            'email',
            'phone',
            'address',
            'password1',
            'password2',
        )

    def clean_tc_id(self):
        tc_id = self.cleaned_data.get('tc_id')

        if not tc_id.isdigit():
            raise forms.ValidationError("TC sadece rakam olmalıdır.")

        if len(tc_id) != 11:
            raise forms.ValidationError("TC 11 haneli olmalıdır.")

        if CustomUser.objects.filter(tc_id=tc_id).exists():
            raise forms.ValidationError("Bu TC zaten kayıtlı.")

        return tc_id

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        digits = ''.join(filter(str.isdigit, phone))

        if len(digits) < 10:
            raise forms.ValidationError("Geçersiz telefon numarası.")

        return phone

    def save(self, commit=True):
        user = super().save(commit=False)

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
    tc_id = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput)

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
    tc_id = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        tc_id = cleaned_data.get("tc_id")
        password = cleaned_data.get("password")

        if tc_id and password:
            try:
                user = CustomUser.objects.get(tc_id=tc_id, user_type="admin")
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Admin bilgileri hatalı.")

            if not user.check_password(password):
                raise forms.ValidationError("Admin bilgileri hatalı.")

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)