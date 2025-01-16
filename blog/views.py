from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from mailing.models import Mailing, Client
from blog.models import BlogPost


def home_view(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='started').count()
    unique_clients = Client.objects.aggregate(count=Count('email', distinct=True))['count']
    random_articles = BlogPost.objects.order_by('?')[:3]

    user_mailings = None
    if request.user.is_authenticated:
        user_mailings = Mailing.objects.filter(owner=request.user)

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'random_articles': random_articles,
        'user_mailings': user_mailings,
    }
    return render(request, 'home.html', context)


def blog_detail_view(request, pk):
    article = get_object_or_404(BlogPost, pk=pk)

    # Увеличиваем просмотры без кэширования
    article.views += 1
    article.save()

    @cache_page(60)
    def cached_article_view(request):
        return render(request, 'blog/blog_detail.html', {'article': article})

    return cached_article_view(request)
