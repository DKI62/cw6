from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

from blog.models import BlogPost
from users.models import CustomUser
from .models import Mailing, Client, Message
from .forms import MailingForm, ClientForm, MessageForm


@cache_page(100)
def cached_home_view(request):
    # Общая информация
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='started').count()
    unique_clients = Client.objects.aggregate(count=Count('email', distinct=True))['count']

    # Рекомендованные статьи
    random_articles = BlogPost.objects.order_by('?')[:3]

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'random_articles': random_articles,
        'user_mailings': None,  # Для анонимных пользователей данные о рассылках не нужны
    }
    return render(request, 'home.html', context)


def home_view(request):
    if request.user.is_authenticated:
        # Не кэшируем для авторизованных пользователей
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status='started').count()
        unique_clients = Client.objects.aggregate(count=Count('email', distinct=True))['count']

        # Рекомендованные статьи
        random_articles = BlogPost.objects.order_by('?')[:3]
        user_mailings = Mailing.objects.filter(owner=request.user)

        context = {
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'unique_clients': unique_clients,
            'random_articles': random_articles,
            'user_mailings': user_mailings,
        }
        return render(request, 'home.html', context)

    # Для анонимных пользователей используем кэшированное представление
    return cached_home_view(request)


# Просмотр списка рассылок только своих
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in.")
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Передача текущего пользователя в форму
        return kwargs

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.instance.owner != self.request.user:
            return HttpResponseForbidden("You don't have permission to edit this mailing.")
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in.")
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientListView(ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in.")
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# Представление для менеджера: просмотр всех рассылок
class MailingAdminListView(UserPassesTestMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_admin_list.html'
    context_object_name = 'mailings'

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def get_queryset(self):
        return Mailing.objects.all()


# Представление для отключения рассылок менеджером
class MailingToggleStatusView(UserPassesTestMixin, UpdateView):
    model = Mailing
    fields = []
    template_name = 'mailing/mailing_toggle_status.html'
    success_url = reverse_lazy('mailing:mailing_admin_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        mailing.status = 'completed'
        mailing.save()
        return super().post(request, *args, **kwargs)


class ClientAdminListView(UserPassesTestMixin, ListView):
    model = Client
    template_name = 'mailing/client_admin_list.html'
    context_object_name = 'clients'

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def get_queryset(self):
        return Client.objects.all()


class MessageAdminListView(UserPassesTestMixin, ListView):
    model = Message
    template_name = 'mailing/message_admin_list.html'
    context_object_name = 'messages'

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def get_queryset(self):
        return Message.objects.all()


class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()
