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


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        """Этот метод не лишний. Лишний тут был has_object_permission"""
        return (request.method in permissions.SAFE_METHODS
                or (request.user and request.user.is_authenticated
                    and request.user.role == 'admin')
                )


class AdminGetOrEditUsers(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
# убрал has_object_permission, потому что этот пермишн нужен на весь вьюсет
