from django.urls import path
from .views import home_view, blog_detail_view

app_name = 'blog'

urlpatterns = [
    path('', home_view, name='home'),
    path('<int:pk>/', blog_detail_view, name='blog_detail'),
]
