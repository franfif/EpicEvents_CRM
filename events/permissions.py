from rest_framework import permissions

from authentication.models import UserRole


class HasEventPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == "POST":
            return request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM)
        return False
        # return request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM)
