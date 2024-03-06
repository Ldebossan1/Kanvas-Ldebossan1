from rest_framework import permissions
from rest_framework.request import Request
from django.views import View


class IsAdminOrGetMethodPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if request.user.is_superuser:
            return True

        return request.method in permissions.SAFE_METHODS


class IsAdminAndAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.is_superuser
