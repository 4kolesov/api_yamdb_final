from rest_framework import serializers
import datetime
from django.conf import settings
from django.db.models import Sum
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, Title, User


class SignUpSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(
        max_length=5,
        write_only=True,
        default=serializers.CreateOnlyDefault)

    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all, message='Email должен быть уникальный!')])

    class Meta:
        model = User
        fields = ['email', 'username', 'confirmation_code']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Username не может быть "me"'
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    role = serializers.ChoiceField(choices=settings.ROLES_CHOICES, read_only=True)

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
    role = serializers.ChoiceField(choices=settings.ROLES_CHOICES, required=False)
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)
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
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.DecimalField(
        max_digits=4, decimal_places=0, max_value=datetime.date.today().year)
    rating = serializers.SerializerMethodField()
    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title

    def get_rating(self, obj):
        count = obj.reviews.count()
        summ = obj.reviews.aggregate(Sum('score'))
        return int(summ['score__sum']/count)
