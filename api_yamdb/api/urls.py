from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet


app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
