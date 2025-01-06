from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJob
from .management.commands.send_newsletter import Command


def send_newsletter_job():
    """
    Функция, которая будет вызываться по расписанию для отправки рассылок.
    """
    command = Command()
    command.handle()


def start_scheduler():
    """
    Запускает планировщик задач.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Попробуем удалить старую задачу, если она существует
    try:
        existing_job = DjangoJob.objects.filter(id="send_newsletter").first()
        if existing_job:
            existing_job.delete()  # Удаляем старую задачу, если она есть
    except Exception as e:
        print(f"Ошибка при удалении задачи send_newsletter: {e}")

    # Добавляем новую задачу
    try:
        scheduler.add_job(
            send_newsletter_job,
            trigger="interval",  # Интервал, можно использовать "cron"
            minutes=5,  # Пример: каждые 5 минут для тестирования
            id="send_newsletter",
            max_instances=1,
        )
    except ConflictingIdError:
        print("Задача с таким ID уже существует, пропускаем добавление.")

    # Запускаем планировщик
    scheduler.start()
    print("Планировщик задач успешно запущен!")
