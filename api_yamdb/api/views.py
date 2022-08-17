from rest_framework import viewsets
from .serializer import CategorySerializer, ReviewSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from api.permissions import ForAuthorAdminModerator

from reviews.models import Review, Title


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (ForAuthorAdminModerator,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (ForAuthorAdminModerator,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
