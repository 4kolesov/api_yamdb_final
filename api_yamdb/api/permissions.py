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
