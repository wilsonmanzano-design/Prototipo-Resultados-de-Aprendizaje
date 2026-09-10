from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    message = "Solo un Administrador puede realizar esta accion."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Administrador').exists()


class EsDocente(BasePermission):
    message = "Solo un Docente puede realizar esta accion."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Docente').exists()