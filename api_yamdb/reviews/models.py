from django.db import models
from users.models import User


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

    def __str__(self):
        return self.text[:10]


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

    def __str__(self):
        return self.text[:10]
