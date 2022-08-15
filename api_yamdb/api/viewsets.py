from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ListCreateDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    """Вьюсет ограниченный отображением списка, созданием и удалением."""
    pass


class CreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    """Только создание объектов."""
    pass


class UpdateRetrieveViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericViewSet):
    """Получение одного экземпляра и его изменение"""
    pass
