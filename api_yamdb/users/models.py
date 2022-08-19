from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import CorrectUsernameAndNotMe


class User(AbstractUser, CorrectUsernameAndNotMe):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    EMAIL = 'Почта'
    ROLE = 'Роль'
    BIO = 'Биография'

    ROLES_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    )

    DEFAULT_USER_ROLE = USER

    bio = models.TextField(
        BIO,
        blank=True,
    )
    role = models.CharField(
        ROLE,
        max_length=max(len(role) for role, show in ROLES_CHOICES),
        default=DEFAULT_USER_ROLE,
        choices=ROLES_CHOICES,
    )
    confirmation_code = models.CharField(
        max_length=settings.MAX_CC_NAME_LENGTH
    )
    email = models.EmailField(
        EMAIL,
        unique=True
    )

    class Meta:
        ordering = ('date_joined',)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username
