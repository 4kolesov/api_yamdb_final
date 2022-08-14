from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from .viewsets import ListCreateDeleteViewSet
from .serializer import CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer
from  reviews.models import Category, Genre, Review, Title
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from api.permissions import ReviewAndCommentsPermission, AdminPermission



class CategoryViewSet(ListCreateDeleteViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminPermission,)


class GenreViewSet(ListCreateDeleteViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminPermission,)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    #permission_classes = (AdminPermission,)
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    """
    def get_queryset(self):
        FILTER_FIELDS = {
            'name': 'name__startswith',
            'year': 'year',
            'category': 'category__slug',
            'genre': 'genre__slug'
        }
        fields = []
        values = []
        for q_field, f_field in FILTER_FIELDS.items():
            field_val = self.request.query_params.get(q_field)
            if field_val is not None:
                fields.append(f_field)
                values.append(field_val)
        return Title.objects.prefetch_related('genre').select_related('category').filter(*zip(fields, values))
    """

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    #permission_classes = (ReviewAndCommentsPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])

        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    #permission_classes = (ReviewAndCommentsPermission,)

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        serializer.save(author=self.request.user, review=review)
