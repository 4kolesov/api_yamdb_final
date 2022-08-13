from rest_framework import serializers
from django.shortcuts import get_object_or_404

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
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review

    def get_title(self):
        return get_object_or_404(
            Title, id=self.context.get("view").kwargs.get("title_id")
        )

    def validate(self, data):
        if (
            Review.objects.filter(
                author=self.context["request"].user, title=self.get_title()
            ).exists()
            and self.context["request"].method != "PATCH"
        ):
            raise serializers.ValidationError(
                "Вы уже оставляли отзыв на это произведение"
            )
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
        fields = ['id', 'text', 'author', 'pub_date', 'review']
        model = Comment
