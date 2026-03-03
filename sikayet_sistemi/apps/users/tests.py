from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserViewsTest(TestCase):
    def test_auth_page_loads(self):
        """Auth sayfası yükleniyor mu"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Giriş Yap")
        self.assertContains(response, "Kayıt Ol")

    def test_register_tab_active(self):
        """Kayıt sayfasından açıldığında kayıt tab'ı aktif"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'register_mode')

    def test_can_register_with_email_and_phone(self):
        """Kullanıcı email ve telefon ile kayıt olabiliyor"""
        data = {
            'username': 'tester',
            'email': 'test@example.com',
            'phone': '+905551234567',
            'password1': 'secret1234',
            'password2': 'secret1234'
        }
        resp = self.client.post(reverse('register'), data)
        self.assertRedirects(resp, reverse('home'))
        # user created
        user = User.objects.get(username='tester')
        self.assertEqual(user.email, 'test@example.com')
        # profile created with phone
        self.assertEqual(user.profile.phone, '+905551234567')

    def test_can_register_and_login(self):
        """Kullanıcı kayıt olup giriş yapabiliyor"""
        data = {
            'username': 'tester',
            'email': 'test@example.com',
            'phone': '+905551234567',
            'password1': 'secret1234',
            'password2': 'secret1234'
        }
        resp = self.client.post(reverse('register'), data)
        self.assertRedirects(resp, reverse('home'))
        # logout then login
        self.client.logout()
        login_data = {'username': 'tester', 'password': 'secret1234'}
        resp2 = self.client.post(reverse('login'), login_data)
        self.assertRedirects(resp2, reverse('home'))

    def test_duplicate_email_rejected(self):
        """Aynı email ile kayıt yapılamıyor"""
        # First user
        data1 = {
            'username': 'user1',
            'email': 'same@example.com',
            'phone': '+905551111111',
            'password1': 'secret1234',
            'password2': 'secret1234'
        }
        self.client.post(reverse('register'), data1)
        # Second user with same email
        data2 = {
            'username': 'user2',
            'email': 'same@example.com',
            'phone': '+905552222222',
            'password1': 'secret1234',
            'password2': 'secret1234'
        }
        resp = self.client.post(reverse('register'), data2, follow=False)
        # Form should show error (status 200 = form redisplayed with error)
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'register_form', 'email', 'Bu e-posta adresi zaten kayıtlı.')

