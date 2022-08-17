from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# from .validators import CorrectUsernameAndNotMe


# class User(AbstractUser, CorrectUsernameAndNotMe):
class User(AbstractUser):

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        default=settings.DEFAUL_USER_ROLE,
        choices=settings.ROLES_CHOICES,
    )
    confirmation_code = models.CharField(
        max_length=256
    )
    email = models.EmailField(
        'Почта',
        unique=True
    )

    class Meta:
        ordering = ('date_joined',)


    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username
