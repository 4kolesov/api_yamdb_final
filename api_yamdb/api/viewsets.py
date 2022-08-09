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