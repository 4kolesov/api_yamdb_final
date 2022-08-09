from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from .viewsets import ListCreateDeleteViewSet
from .serializer import CategorySerializer, GenreSerializer
from  reviews.models import Category, Genre


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
