from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    is_verified = models.BooleanField(default=False, verbose_name='Подтверждённый Email')

    def __str__(self):
        return self.username
