from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (AdminGetOrEditUsers, ForAdminPermission,
                             ReviewAndCommentsPermission)
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
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (ForAdminPermission,)


class GenreViewSet(ListCreateDeleteViewSet):
    """Вьюсет для модели жанров."""
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (ForAdminPermission,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели произведений."""
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (ForAdminPermission,)
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (ReviewAndCommentsPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])

        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewAndCommentsPermission,)

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        serializer.save(author=self.request.user, review=review)


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
        message = f'Ваш код авторизации {confirmation_code}. Наслаждайтесь!'
        send_mail(
            'Верификация YaMDB', message, settings.ADMIN_EMAIL, [user.email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as error:
        print(f'Такой username или email уже заняты: {error}!')


@api_view(['POST'])
def get_token(request):
    """Выдача токена в ответ на код подтверждения и юзернейм."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user and user.confirmation_code == confirmation_code:
            refresh = RefreshToken.for_user(user)
            return Response(
                str(refresh.access_token), status=status.HTTP_200_OK
            )
    except ValidationError as error:
        raise ValidationError(error)

    except Exception as error:
        print(f'Отсутствуют обязательные поля для запроса токена: {error}!')



# @api_view(['POST'])
# def get_token(request):
#     """Выдача токена в ответ на код подтверждения и юзернейм."""
#     serializer = TokenSerializer(data=request.data)
#     if serializer.is_valid(raise_exception=True):
#         username = serializer.validated_data['username']
#         confirmation_code = serializer.validated_data['confirmation_code']
#         user = get_object_or_404(User, username=username)
#         if user and user.confirmation_code == confirmation_code:
#             refresh = RefreshToken.for_user(user)
#             return Response(
#                 str(refresh.access_token), status=status.HTTP_200_OK
#             )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Юзеры для админа + детали и редактирование о себе."""
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        AdminGetOrEditUsers,
    )
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
        if request.method == 'PATCH':
            user = User.objects.get(username=self.request.user)
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = UserSerializer(user)
        return Response(serializer.data)
