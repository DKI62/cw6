import time

from django.core.management.base import BaseCommand
from mailing.apscheduler import start_scheduler


class Command(BaseCommand):
    help = "Запускает планировщик задач (APSCHEDULER)"

    def handle(self, *args, **options):
        start_scheduler()
        self.stdout.write(self.style.SUCCESS("Планировщик задач запущен!"))

        # Блокируем основной поток, чтобы планировщик не закрылся
        try:
            while True:
                time.sleep(60)  # каждые 60с можно «дремать»
        except KeyboardInterrupt:
            print("Останавливаем планировщик...")
