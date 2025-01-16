from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    # Маршруты для рассылок
    path('', views.MailingListView.as_view(), name='mailing_list'),
    path('create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_edit'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),

    # Маршруты для клиентов
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),

    # Маршруты для сообщений
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),

    # Маршруты для менеджеров
    path('admin/', views.MailingAdminListView.as_view(), name='mailing_admin_list'),
    path('admin/<int:pk>/toggle/', views.MailingToggleStatusView.as_view(), name='mailing_toggle_status'),
    path('admin/clients/', views.ClientAdminListView.as_view(), name='client_admin_list'),
    path('admin/messages/', views.MessageAdminListView.as_view(), name='message_admin_list'),
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
]
