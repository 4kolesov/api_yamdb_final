from rest_framework import viewsets
from .viewsets import ListCreateDeleteViewSet
from .serializer import CategorySerializer
from  reviews.models import Category


class CategoryViewSet(ListCreateDeleteViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
