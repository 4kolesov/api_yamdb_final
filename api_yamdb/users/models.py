from datetime import datetime, timedelta
import jwt

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Для кастомных моделей обязателен."""

    def create_user(self, username, email, confirmation_code):
        """Создает и возвращает пользователя с почтой, именем и кодом."""
        if username is None:
            raise TypeError('У пользователя должно быть уникальное имя.')
        if email is None:
            raise TypeError(
                'У пользователя должен быть уникальный адрес электронной почты'
            )
        user = self.model(
            confirmation_code=confirmation_code,
            username=username,
            email=self.normalize_email(email)
        )
        user.save()
        return user

    def create_superuser(self, username, email, password):
        """Создает суперпользователя."""
        if password is None:
            raise TypeError('Суперпользователь должен иметь пароль.')
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


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
    confirmation_code = models.CharField(
        max_length=256
    )

    objects = UserManager()


    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=14)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
