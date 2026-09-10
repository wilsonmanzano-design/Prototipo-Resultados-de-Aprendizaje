from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UsuarioSerializer
from .permissions import EsAdministrador


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ObtenerCsrfView(APIView):
    """React llama esto UNA vez al cargar la app para recibir la cookie csrftoken."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'detail': 'Cookie CSRF establecida.'})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Credenciales invalidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response(UsuarioSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Sesion cerrada.'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class SoloAdminPingView(APIView):
    """Endpoint de prueba para verificar que el permiso EsAdministrador funciona.
    Sirve además de plantilla para futuros endpoints solo-admin (Fase 5 y 9)."""
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]

    def get(self, request):
        return Response({'detail': 'Acceso de administrador confirmado.'})