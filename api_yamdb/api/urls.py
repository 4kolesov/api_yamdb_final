from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet, CommentViewSet, ReviewViewSet

from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, SignUpViewSet,
                    GetTokenView, UserViewSet)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('auth/signup', SignUpViewSet, basename='signup')
router_v1.register('users', UserViewSet, basename='users')
router = SimpleRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
]
