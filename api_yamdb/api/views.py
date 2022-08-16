from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (
    AdminPermission,
    ForAdminPermission,
    ReviewAndCommentsPermission)
from reviews.models import Category, Genre, Review, Title, User
from users.utils import generate_confirmation_code

from .filters import TitleFilter
from .serializer import (AdminSerializer, CategorySerializer,
                         CommentSerializer, GenreSerializer, ReviewSerializer,
                         SignUpSerializer, TitleSerializer, TokenSerializer,
                         UserSerializer)
from .viewsets import CreateViewSet, ListCreateDeleteViewSet


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

class SignUpViewSet(CreateViewSet):
    """Регистрация пользователя и отправка кода подтверждения на почту."""
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # return User.objects.all()
        return User.objects.get_or_create()

    def perform_create(self, serializer):
        user = self.request.data['username']
        email = self.request.data['email']
        confirmation_code = generate_confirmation_code()
        message = f'Ваш код авторизации {confirmation_code}. Наслаждайтесь!'
        send_mail('Верификация YaMDB', message, 'admin@yamdb.ru', [email])
        return serializer.save(
            username=user,
            email=email,
            confirmation_code=confirmation_code
        )


class GetTokenView(generics.GenericAPIView):
    """Выдача токена в ответ на код подтверждения и юзернейм."""
    serializer_class = TokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = self.request.data.get('username')
        confirmation_code = self.request.data.get('confirmation_code')
        user = User.objects.get(
            username=username,
            confirmation_code=confirmation_code
        )
        refresh = RefreshToken.for_user(user)
        return Response(str(refresh.access_token))


class UserViewSet(ModelViewSet):
    """Юзеры для админа + детали и редактирование о себе."""
    serializer_class = AdminSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        permissions.IsAuthenticated,
        AdminPermission
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
