from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

from .validators import max_year


def year_max():
    return date.today().year


class CGAbstract(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_CG_NAME_LENGTH
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=settings.MAX_CG_SLUG_LENGTH
    )

    class Meta:
        ordering = ('name',)
        abstract = True

    def __str__(self):
        return self.name


class Genre(CGAbstract):
    class Meta(CGAbstract.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(CGAbstract):
    class Meta(CGAbstract.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_TITLE_NAME_LENGTH,
    )
    year = models.PositiveSmallIntegerField(
        'Год создания',
        db_index=True,
        validators=(max_year,)
    )
    description = models.TextField(
        'Описание',
        blank=True
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='titles',
        null=True
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр',
        related_name='titles'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = (
            models.CheckConstraint(
                check=models.Q(year__lte=year_max()),
                name='year_check'
            ),
        )


class CRAbstract(models.Model):
    """Абстрактная модель для комменатриев и ревью."""
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:10]


class Review(CRAbstract):

    title = models.ForeignKey(
        'Title',
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )

    class Meta(CRAbstract.Meta):
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(CRAbstract):
    review = models.ForeignKey(
        'Review',
        verbose_name='Ревью',
        on_delete=models.CASCADE
    )

    class Meta(CRAbstract.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
