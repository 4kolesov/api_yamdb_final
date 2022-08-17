from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from api.permissions import IsAdminOrReadOnly


class ListCreateDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    """Вьюсет ограниченный отображением списка, созданием и удалением."""
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class CreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    """Только создание объектов."""
    pass


class UpdateRetrieveViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericViewSet):
    """Получение одного экземпляра и его изменение"""
    pass
