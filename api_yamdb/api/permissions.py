from rest_framework import permissions


class ReviewAndCommentsPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        self.message = 'Необходимо авторизоваться'
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        self.message = 'Доступно только автору'
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role in ['admin', 'moderator'])


class AdminPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
        or (request.user and request.user.is_authenticated
            and request.user.role=='admin'))

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or (request.user
            and request.user.is_authenticated and request.user.role=='admin')
        )
