from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        default='user',
        choices=settings.ROLES_CHOICES,
    )
    confirmation_code = models.CharField(
        max_length=256
    )
    email = models.EmailField(
        'Почта',
        unique=True
    )
