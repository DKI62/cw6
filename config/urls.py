from django.contrib import admin
from django.urls import path, include

from mailing.views import HomePageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),  # Главная страница
    path('mailing/', include('mailing.urls')),  # подключаем маршруты нашего приложения
]
