from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError
from mailing.models import Mailing, Client, Attempt
from django.utils.timezone import now
import smtplib
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка рассылок'

    def handle(self, *args, **kwargs):
        logger.info("Начало отправки рассылок")
        # Получаем все рассылки, которые нужно отправить
        mailings = Mailing.objects.filter(
            status='started',
            start_time__lte=now()
        )

        for mailing in mailings:
            subject = mailing.message.subject
            body = mailing.message.body

            # Счётчик успешных отправок
            success_count = 0

            # Для каждой рассылки отправляем email всем клиентам
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject,
                        body,
                        'dm1task@yandex.ru',  # Ваш email отправителя
                        [client.email],
                        fail_silently=False,  # Чтобы при ошибках вызывать исключение
                    )
                    # Записываем удачную попытку
                    Attempt.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response='Письмо успешно отправлено'
                    )
                    success_count += 1

                except BadHeaderError as e:
                    # Ошибка заголовка
                    Attempt.objects.create(
                        mailing=mailing,
                        status='failed',
                        server_response=f"BadHeaderError: {e}"
                    )
                    logger.error(f"BadHeaderError при отправке рассылки '{mailing.title}' клиенту {client.email}: {e}")
                except smtplib.SMTPException as e:
                    # Почтовый сервер вернул ошибку
                    Attempt.objects.create(
                        mailing=mailing,
                        status='failed',
                        server_response=f"SMTPException: {e}"
                    )
                    logger.error(f"SMTPException при отправке рассылки '{mailing.title}' клиенту {client.email}: {e}")
                except Exception as e:
                    # Любая другая ошибка
                    Attempt.objects.create(
                        mailing=mailing,
                        status='failed',
                        server_response=f"Error: {e}"
                    )
                    logger.error(f"Ошибка при отправке рассылки '{mailing.title}' клиенту {client.email}: {e}")

            # Обработка статуса рассылки и обновление start_time
            if success_count > 0:
                # Обновляем start_time и сохраняем статус
                if mailing.periodicity == 'daily':
                    mailing.start_time += timedelta(days=1)
                elif mailing.periodicity == 'weekly':
                    mailing.start_time += timedelta(weeks=1)
                elif mailing.periodicity == 'monthly':
                    mailing.start_time += relativedelta(months=1)
                else:
                    # Если периодичность не задана, завершить рассылку
                    mailing.status = 'completed'

                # Если периодичность задана, оставляем статус 'started', иначе 'completed'
                if mailing.periodicity in ['daily', 'weekly', 'monthly']:
                    mailing.status = 'started'
                else:
                    mailing.status = 'completed'

                mailing.save()
                logger.info(f"Рассылка '{mailing.title}' успешно обработана и обновлена.")
            else:
                # Если не удалось отправить ни одно письмо, можно оставить статус 'started' или изменить его
                # Здесь оставим статус 'started' для повторных попыток
                mailing.status = 'started'
                mailing.save()
                logger.info(f"Рассылка '{mailing.title}' обработана с ошибками, статус оставлен 'started'.")

        self.stdout.write(self.style.SUCCESS('Все рассылки обработаны!'))
        logger.info("Все рассылки обработаны.")
