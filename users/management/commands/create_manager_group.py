from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing, Client, Message
from users.models import CustomUser


class Command(BaseCommand):
    help = "Создает группу менеджеров с необходимыми правами"

    def handle(self, *args, **kwargs):
        manager_group, created = Group.objects.get_or_create(name='Manager')

        # Права для рассылок
        mailing_content_type = ContentType.objects.get_for_model(Mailing)
        client_content_type = ContentType.objects.get_for_model(Client)
        message_content_type = ContentType.objects.get_for_model(Message)
        user_content_type = ContentType.objects.get_for_model(CustomUser)

        permissions = [
            {'content_type': mailing_content_type, 'codename': 'view_mailing'},
            {'content_type': mailing_content_type, 'codename': 'change_mailing'},
            {'content_type': client_content_type, 'codename': 'view_client'},
            {'content_type': message_content_type, 'codename': 'view_message'},
            {'content_type': user_content_type, 'codename': 'view_customuser'},
            {'content_type': user_content_type, 'codename': 'change_customuser'},
        ]

        for perm in permissions:
            try:
                permission = Permission.objects.get(
                    content_type=perm['content_type'],
                    codename=perm['codename']
                )
                manager_group.permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'Добавлено разрешение: {perm["codename"]}'))
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Разрешение {perm["codename"]} не найдено'))

        self.stdout.write(self.style.SUCCESS('Группа "Manager" успешно создана с необходимыми правами!'))
