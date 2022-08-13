from rest_framework import serializers
import datetime
from django.db.models import Sum

from reviews.models import Category, Genre, Title, User


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
