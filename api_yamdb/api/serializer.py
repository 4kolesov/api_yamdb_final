import datetime

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.validators import MaxYear

from reviews.models import Category, Comment, Genre, Review, Title, User

from .fields import (ToSerializerInSlugManyRelatedField,
                     ToSerializerInSlugRelatedField)


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Username не может быть "me"'
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, write_only=True)
    confirmation_code = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    role = serializers.ChoiceField(
        choices=settings.ROLES_CHOICES, read_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        ]


class AdminSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=settings.ROLES_CHOICES, required=False)
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email должен быть уникальный!')],
        required=True,
        max_length=150
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email должен быть уникальный!')],
        required=True,
        max_length=254
    )
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        ]


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
        validators = (MaxYear(field='year'),)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review

    def get_title(self):
        return get_object_or_404(
            Title, id=self.context.get('view').kwargs.get('title_id')
        )

    def validate(self, data):
        if (
            Review.objects.filter(
                author=self.context.get('request').user, title=self.get_title()
            ).exists()
            and self.context.get('request').method != 'PATCH'
        ):
            raise serializers.ValidationError(
                "Нельзя оставить отзыв на одно произведение дважды"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment
