from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'views')
    search_fields = ('title', 'content')
    list_filter = ('published_date',)
    readonly_fields = ('views', 'published_date')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если это новая статья
            obj.author = request.user  # Установить текущего пользователя как автора
        super().save_model(request, obj, form, change)