from django.apps import AppConfig


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'

    def ready(self):
        """
        Оставляем метод ready() пустым, чтобы избежать
        автоматического запуска планировщика при инициализации приложения.
        """
        pass
