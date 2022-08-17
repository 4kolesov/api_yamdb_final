from django.db import models
from django.core.validators import MaxValueValidator
from datetime import date
from django.db.models import F, Q

from users.models import User



def year_max():
    return date.today().year


class CGAbstract(models.Model):
    name = models.CharField(
        'Название',
        max_length=256
    )
    slug = models.SlugField(
        'Slug',
        unique=True
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
        max_length=250,
    )
    year = models.PositiveSmallIntegerField(
        'Год создания',
        db_index=True,
        validators=(MaxValueValidator(
            limit_value=year_max,
            message='Год выпуска не может быть больше текущего'),
        )
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
                check=Q(year__lte=year_max()),
                name='year_check'
            ),
        )


class Review(models.Model):
    SCORE_CHOICES = list(zip(range(11), range(11)))

    title = models.ForeignKey(
        'Title',
        verbose_name='Произведение',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Ревью',
        blank=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор ревью',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    score = models.IntegerField(
        'Оценка',
        choices=SCORE_CHOICES,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        'Review',
        verbose_name='Ревью',
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Комментарий'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        related_name='comments',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
