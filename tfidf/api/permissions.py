from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):

    def has_permission(self, request, obj):
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        if request.method in ['PATCH', 'DELETE', 'PUT']:
            return obj == request.user or request.user.is_staff
        return True
