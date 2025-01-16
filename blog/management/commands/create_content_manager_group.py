from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost


class Command(BaseCommand):
    help = "Создает группу ContentManager с необходимыми правами"

    def handle(self, *args, **kwargs):
        content_manager_group, created = Group.objects.get_or_create(name='ContentManager')
        blogpost_content_type = ContentType.objects.get_for_model(BlogPost)

        permissions = Permission.objects.filter(content_type=blogpost_content_type)
        content_manager_group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS('Группа ContentManager успешно создана с правами!'))
