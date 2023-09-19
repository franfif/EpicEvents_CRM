from rest_framework import permissions

from authentication.models import UserRole


class IsSalesTeamMemberOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM)
