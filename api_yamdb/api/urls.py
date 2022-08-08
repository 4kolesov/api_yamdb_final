from django.urls import include, path
from rest_framework.routers import SimpleRouter

from views import CategoryViewSet


app_name = 'api'

router = SimpleRouter()
router.register('categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('v1/', include(router.urls)),
]