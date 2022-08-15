from rest_framework import permissions


class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.role == 'admin'
