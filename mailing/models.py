from django.db import models


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]
    PERIOD_CHOICES = [
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    ]
    title = models.CharField(max_length=255)  # Добавляем поле title
    start_time = models.DateTimeField()
    periodicity = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings")
    clients = models.ManyToManyField(Client, related_name="mailings")

    def __str__(self):
        return f"Рассылка {self.title} - {self.get_status_display()}"


class Attempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Неуспешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус отправки')
    server_response = models.TextField(blank=True, null=True, verbose_name='Ответ почтового сервера')

    def __str__(self):
        return f"Попытка рассылки «{self.mailing.title}» — {self.get_status_display()} от {self.sent_at}"
