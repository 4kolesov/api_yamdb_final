from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Review, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = (id,)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = (id,)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name',)
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError(
                'Оцените произведение от 0 до 10')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
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
