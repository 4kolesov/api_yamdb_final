from rest_framework import viewsets
# from rest_framework import generics
# from rest_framework import serializers
# from rest_framework.response import Response
# from rest_framework import status
from rest_framework.filters import SearchFilter
from .viewsets import ListCreateDeleteViewSet
from .serializer import (CategorySerializer,
                         GenreSerializer,
                         TitleSerializer,
                         SignUpSerializer)
from .viewsets import CreateViewSet
from reviews.models import Category, Genre, Title, User
from users.utils import generate_confirmation_code
from django.core.mail import send_mail


class CategoryViewSet(ListCreateDeleteViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDeleteViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()


class SignUpViewSet(CreateViewSet):
    # queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def get_queryset(self):
        return User.objects.all()

    def perform_create(self, serializer):
        user = self.request.data['username']
        email = self.request.data['email']
        confirmation_code = generate_confirmation_code()
        message = f'Ваш код авторизации {confirmation_code}. Наслаждайтесь!'
        send_mail('Верификация YaMDB', message, 'admin@yamdb.ru', [email])
        return serializer.save(username=user, email=email, confirmation_code=confirmation_code)
