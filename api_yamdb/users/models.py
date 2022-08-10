from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
import jwt
from datetime import datetime, timedelta
from django.conf import settings


class UserManager(BaseUserManager):
    """Для кастомных моделей обязателен."""

    def create_user(self, username, email, password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('У пользователя должно быть уникальное имя.')
        if email is None:
            raise TypeError(
                'У пользователя должен быть уникальный адрес электронной почты'
            )
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password):
        """Создает суперпользователя"""
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

    objects = UserManager()
