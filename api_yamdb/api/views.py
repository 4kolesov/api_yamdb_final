from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

import api.permissions
from reviews.models import Category, Genre, Title, User
from users.utils import generate_confirmation_code
from .serializer import (CategorySerializer,
                         GenreSerializer,
                         TitleSerializer,
                         SignUpSerializer,
                         TokenSerializer,
                         UserSerializer,
                         AdminSerializer)
from .viewsets import ListCreateDeleteViewSet


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_user(request):
    """Регистрация пользователя, генерирование и отправка код подтверждения."""
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        confirmation_code = generate_confirmation_code()
        user, stat = User.objects.get_or_create(
            **serializer.validated_data,
            confirmation_code=confirmation_code
        )
        message = f'Ваш код авторизации {confirmation_code}. Наслаждайтесь!'
        send_mail('Верификация YaMDB', message, settings.ADMIN_EMAIL, [user.email])
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Выдача токена в ответ на код подтверждения и юзернейм."""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user and user.confirmation_code == confirmation_code:
            refresh = RefreshToken.for_user(user)
            return Response(str(refresh.access_token), status=status.HTTP_200_OK)



    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    """Юзеры для админа + детали и редактирование о себе."""
    serializer_class = AdminSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        permissions.IsAuthenticated,
        api.permissions.AdminPermission
    ]
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username']

    def get_queryset(self):
        return User.objects.all()

    @action(
        methods=['get', 'patch'],
        detail=False, url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_patch_users_me(self, request):
        user = User.objects.get(username=self.request.user)
        if request.method == 'PATCH':
            user = User.objects.get(username=self.request.user)
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = UserSerializer(user)
        return Response(serializer.data)
