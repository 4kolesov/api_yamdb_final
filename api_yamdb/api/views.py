from django.core.mail import send_mail
from rest_framework import generics, viewsets, permissions
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from reviews.models import Category, Genre, Title, User
from users.utils import generate_confirmation_code
from .serializer import (CategorySerializer,
                         GenreSerializer,
                         TitleSerializer,
                         SignUpSerializer,
                         TokenSerializer,
                         UserSerializer)
from .viewsets import (CreateViewSet,
                       ListCreateDeleteViewSet,
                       UpdateRetrieveViewSet)


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
    """Регистрация пользователя и отправка кода подтверждения на почту."""
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


class GetTokenView(generics.GenericAPIView):
    """Выдача токена в ответ на код подтверждения и юзернейм."""
    serializer_class = TokenSerializer

    def post(self, request):
        username = self.request.data.get('username')
        confirmation_code = self.request.data.get('confirmation_code')
        user = User.objects.get(
            username=username,
            confirmation_code=confirmation_code
        )
        refresh = RefreshToken.for_user(user)
        return Response(str(refresh.access_token))


class UserViewSet(UpdateRetrieveViewSet):
    """Детали о конкретном юзере и изменение информации о себе."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

    @action(methods=['get', 'patch'], detail=False, url_path='me')
    def get_users_me(self, request):
        if request.method == 'patch':
            user = User.objects.filter(username=self.request.user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        user = User.objects.filter(username=self.request.user)
        serializer = self.get_serializer(user, many=True)
        return Response(serializer.data)

    # @action(detail=False, url_path='me')
    # def get_users_me(self, request):
    #     user = User.objects.filter(username=self.request.user)
    #     serializer = self.get_serializer(user, many=True)
    #     return Response(serializer.data)

    # @action(detail=False, url_path='me')
    # def perform_update(self, serializer):
    #     return serializer.save
