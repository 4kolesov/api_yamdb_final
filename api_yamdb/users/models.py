from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLES_CHOICES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Админ'),
    )

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        default='user',
        choices=ROLES_CHOICES,
    )
