from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from .viewsets import ListCreateDeleteViewSet
from .serializer import CategorySerializer
from  reviews.models import Category


class CategoryViewSet(ListCreateDeleteViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
