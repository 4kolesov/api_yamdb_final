from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet,
                    GetTokenView, UserViewSet)
# from .views import SignUpViewSet
from .views import signup_user

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
# router_v1.register('auth/signup', SignUpViewSet, basename='signup')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
    path('v1/auth/signup/', signup_user, name='signup'),
]
