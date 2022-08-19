from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (AdminGetOrEdit, IsAdminOrReadOnly,
                             IsAuthorAdminModerator)
from reviews.models import Category, Genre, Review, Title, User
from users.utils import generate_confirmation_code

from .filters import TitleFilter
from .serializer import (AdminSerializer, CategorySerializer,
                         CommentSerializer, GenreSerializer, ReviewSerializer,
                         SignUpSerializer, TitleSerializer, TokenSerializer,
                         UserSerializer)
from .viewsets import ListCreateDeleteViewSet

Users = get_user_model()


class CategoryViewSet(ListCreateDeleteViewSet):
    """Вьюсет для модели категории."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GenreViewSet(ListCreateDeleteViewSet):
    """Вьюсет для модели жанров."""
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели произведений."""
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filterset_class = TitleFilter
    ordering = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModerator,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModerator,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


@api_view(['POST'])
def signup_user(request):
    """Регистрация пользователя, генерирование и отправка код подтверждения."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        confirmation_code = str(generate_confirmation_code())
        user, stat = User.objects.get_or_create(
            **serializer.validated_data,
            confirmation_code=confirmation_code
        )
    except IntegrityError as error:
        raise ValidationError(
            f'Ошибка! Это имя пользователя или email уже существуют: {error}')
    message = f'Ваш код авторизации {confirmation_code}. Наслаждайтесь!'
    send_mail(
        'Верификация YaMDB', message, settings.ADMIN_EMAIL, [user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    """Выдача токена в ответ на код подтверждения и юзернейм."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if (user.confirmation_code != ' '
            and user.confirmation_code == confirmation_code):
        refresh = RefreshToken.for_user(user)
        user.confirmation_code = ' '
        user.save()
        return Response(
            str(refresh.access_token), status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Юзеры для админа + детали и редактирование о себе."""
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (AdminGetOrEdit,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False, url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_patch_users_me(self, request):
        user = User.objects.get(username=self.request.user)
        serializer = UserSerializer(user)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
