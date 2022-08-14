import datetime

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignUpSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(
        max_length=5,
        write_only=True,
        default=serializers.CreateOnlyDefault)

    class Meta:
        model = User
        fields = ['email', 'username', 'confirmation_code']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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
    role = serializers.CharField(read_only=True)

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
    role = serializers.CharField(required=True)
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


class GenreTitleField(serializers.ManyRelatedField):
    def to_internal_value(self, data):
        return [get_object_or_404(Genre, slug=slug) for slug in data]


class CategoryTitleField(serializers.RelatedField):
    def to_representation(self, value):
        return CategorySerializer(value).data

    def to_internal_value(self, data):
        return get_object_or_404(Category, slug=data)


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(
        min_value=0, max_value=datetime.date.today().year)
    rating = serializers.SerializerMethodField(read_only=True)
    genre = GenreTitleField(child_relation=GenreSerializer())
    category = CategoryTitleField(queryset=Category)
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
        model = Review
        fields = '__all__'

    def validate(self, data):
        review_exists= Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')).exists()
        if review_exists and self.context['request'].method == 'POST':
            raise serializers.ValidationError(
                'Ошибка. Можно оставить только один отзыв.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
