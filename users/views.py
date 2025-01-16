from django.conf import settings
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser
from django.shortcuts import redirect, render

User = get_user_model()


class EmailVerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return HttpResponse('Email успешно подтвержден! Теперь вы можете войти в свой аккаунт.')
        else:
            return HttpResponse('Ссылка для подтверждения недействительна или устарела.', status=400)


class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            return HttpResponse('Все поля обязательны', status=400)

        if User.objects.filter(email=email).exists():
            return HttpResponse('Пользователь с таким Email уже существует.', status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_verified=False
        )

        # Генерация ссылки для подтверждения
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = request.build_absolute_uri(f'/users/verify/{uid}/{token}/')

        # Отправка письма
        send_mail(
            'Подтверждение Email',
            f'Перейдите по ссылке для подтверждения Email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return HttpResponse('На ваш Email отправлена ссылка для подтверждения.')


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomUserLoginForm

    def get_success_url(self):
        return reverse_lazy('home')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class UserProfileView(UpdateView):
    model = CustomUser
    template_name = 'users/profile.html'
    form_class = CustomUserUpdateForm

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user


class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()


# Блокировка пользователя
class UserBlockView(UserPassesTestMixin, View):
    template_name = 'users/user_block_confirm.html'
    success_url = reverse_lazy('users:user_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def get(self, request, *args, **kwargs):
        """Отображение страницы подтверждения блокировки."""
        user = CustomUser.objects.get(pk=kwargs['pk'])
        if user == self.request.user:
            return HttpResponseForbidden("Вы не можете заблокировать самого себя.")
        return render(request, self.template_name, {'object': user})

    def post(self, request, *args, **kwargs):
        """Обработка подтверждения блокировки."""
        user = CustomUser.objects.get(pk=kwargs['pk'])
        if user == self.request.user:
            return HttpResponseForbidden("Вы не можете заблокировать самого себя.")

        # Выполнение блокировки
        user.is_active = False
        user.save()
        return redirect(self.success_url)
