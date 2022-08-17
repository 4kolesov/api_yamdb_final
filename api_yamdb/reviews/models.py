from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    name = models.CharField(
        'Категория',
        max_length=256
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )


class Genre(models.Model):
    name = models.CharField(
        'Жанр',
        max_length=256
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )


class Title(models.Model):
    name = models.CharField(
        'Название',
        max_length=250,
    )
    year = models.DecimalField(
        'Год создания',
        max_digits=4,
        decimal_places=0
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
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр',
        related_name='titles',
        blank=True
    )


class CRAbstract(models.Model):
    """Абстрактная модель для комменатриев и ревью."""
    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        related_name='%(class)s',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.text[:10]


class Review(CRAbstract):

    title = models.ForeignKey(
        'Title',
        verbose_name='Произведение',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
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
        related_name='comments',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
