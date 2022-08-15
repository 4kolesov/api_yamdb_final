from rest_framework import serializers
import datetime
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, Review, Comment, User


class SignUpSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'token']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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


class GenreTitleField(serializers.ManyRelatedField):
    """Поле отображения категорий в произведениях."""
    def to_internal_value(self, data):
        return [get_object_or_404(Genre, slug=slug) for slug in data]


class CategoryTitleField(serializers.SlugRelatedField):
    """Поле отображения категорий в произведениях."""
    def to_representation(self, value):
        return CategorySerializer(value).data


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор отображения и создания произведений."""
    year = serializers.IntegerField(
        min_value=0, max_value=datetime.date.today().year)
    rating = serializers.SerializerMethodField(read_only=True)
    genre = GenreTitleField(child_relation=GenreSerializer())
    category = CategoryTitleField(
        queryset=Category.objects.all(), slug_field='slug')
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
