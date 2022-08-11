from rest_framework import serializers
import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, Review, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class GenreTitleField(serializers.ManyRelatedField):
    def to_representation(self, iterable):
        return [
            self.child_relation.to_representation(value)
            for value in iterable
        ]

    def to_internal_value(self, data):
        return data


class CategoryTitleField(serializers.RelatedField):
    def to_representation(self, value):
        return CategorySerializer(value).data

    def to_internal_value(self, data):
        return data


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.DecimalField(
        max_digits=4, decimal_places=0, max_value=datetime.date.today().year)
    rating = serializers.SerializerMethodField(read_only=True)
    genre = GenreTitleField(child_relation=GenreSerializer())
    category = CategoryTitleField(queryset=Category)
    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title

    def get_rating(self, obj):
        count = obj.reviews.count()
        if count == 0:
            return 0
        summ = obj.reviews.aggregate(Sum('score'))
        return int(summ['score__sum']/count)

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category = get_object_or_404(
            Category, slug=validated_data.pop('category')
        )
        title = Title.objects.create(**validated_data, category=category)
        for genre_slug in genres:
            genre = get_object_or_404(Genre, slug=genre_slug)
            title.genre.add(genre)
        return title

    def update(self, instance, validated_data):
        genres = validated_data.pop('genre')
        category = get_object_or_404(
            Category, slug=validated_data.pop('category')
        )
        instance.genre.clear()
        for genre_slug in genres:
            genre = get_object_or_404(Genre, slug=genre_slug)
            instance.genre.add(genre)
        instance.category = category
        instance.save()
        return instance


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
