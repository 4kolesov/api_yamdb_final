import datetime

from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User

from .fields import (ToSerializerInSlugManyRelatedField,
                     ToSerializerInSlugRelatedField)

from users.utils import regex_test


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email должен быть уникальный!')],
        required=True,
        max_length=254
    )
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9.@+-_]+$',
            ),
            UniqueValidator(
                queryset=User.objects.all(),
                message='Username должен быть уникальный!'),
        ],
        required=True,
        max_length=150
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Username не может быть "me"'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9.@+-_]+$',
            ),
        ],
        required=True,
        write_only=True,
        max_length=150
    )
    confirmation_code = serializers.CharField(
        required=True, write_only=True, max_length=5)


class AdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Username должен быть уникальный!')],
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
    year = serializers.IntegerField(
        min_value=0, max_value=datetime.date.today().year)
    rating = serializers.SerializerMethodField(read_only=True)
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

    def get_rating(self, obj):
        if obj.reviews.count() == 0:
            return None
        return obj.reviews.aggregate(Avg('score'))['score__avg']


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
