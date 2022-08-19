from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import max_year
from users.validators import CorrectUsernameAndNotMe

from .fields import (ToSerializerInSlugManyRelatedField,
                     ToSerializerInSlugRelatedField)


class SignUpSerializer(serializers.Serializer, CorrectUsernameAndNotMe):
    email = serializers.EmailField(
        required=True,
        max_length=settings.MAX_EMAIL_NAME_LENGTH
    )
    username = serializers.CharField(
        required=True,
        max_length=settings.MAX_USERNAME_NAME_LENGTH
    )

    class Meta:
        model = User
        fields = ('email', 'username')


class TokenSerializer(serializers.Serializer, CorrectUsernameAndNotMe):
    username = serializers.CharField(
        required=True,
        write_only=True,
        max_length=settings.MAX_USERNAME_NAME_LENGTH
    )
    confirmation_code = serializers.CharField(
        required=True, write_only=True, max_length=settings.MAX_CC_NAME_LENGTH)


class AdminSerializer(serializers.ModelSerializer, CorrectUsernameAndNotMe):
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Username должен быть уникальный!'),
        ],
        required=True,
        max_length=settings.MAX_USERNAME_NAME_LENGTH
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email должен быть уникальный!')],
        required=True,
        max_length=settings.MAX_EMAIL_NAME_LENGTH
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class UserSerializer(AdminSerializer):
    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор отображения и создания категорий."""
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор отображения и создания жанров."""
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор отображения и создания произведений."""
    year = serializers.IntegerField()
    rating = serializers.IntegerField(read_only=True)
    genre = ToSerializerInSlugManyRelatedField(
        child_relation=GenreSerializer(),
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = ToSerializerInSlugRelatedField(
        serializer=CategorySerializer,
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title
        validators = (max_year,)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            author = request.user
            title_id = self.context.get('view').kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError(
                    'Нельзя оставить отзыв на одно произведение дважды')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
