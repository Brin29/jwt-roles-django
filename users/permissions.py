from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'
    
class IsCliente(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'CLIENTE'