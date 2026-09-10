from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    message = "Solo un Administrador puede realizar esta accion."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Administrador').exists()


class EsDocente(BasePermission):
    message = "Solo un Docente puede realizar esta accion."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Docente').exists()

class EsDocenteDeLaOferta(BasePermission):
    """Permite la accion si el usuario es Administrador, o si es el Docente dueño de la oferta."""
    message = "No tienes permiso sobre esta oferta academica."

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Administrador').exists():
            return True
        oferta = obj if hasattr(obj, 'docente') else obj.oferta
        return hasattr(request.user, 'docente') and oferta.docente_id == request.user.docente.id