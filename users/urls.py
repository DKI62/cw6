from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    EmailVerificationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<uidb64>/<token>/', EmailVerificationView.as_view(), name='email_verify'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', views.UserBlockView.as_view(), name='user_block'),
    # Маршруты для смены пароля
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
]
