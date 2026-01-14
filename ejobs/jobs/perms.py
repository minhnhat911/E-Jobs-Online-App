from rest_framework import permissions

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'EMPLOYER'

class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CANDIDATE'

class OwnerAuthenticated(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.user