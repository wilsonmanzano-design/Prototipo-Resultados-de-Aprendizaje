from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UsuarioSerializer
from .permissions import EsAdministrador
from rest_framework.decorators import action

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

from rest_framework import viewsets
from .models import Programa, Curso, Rap, Rac, Modalidad, Corte, Grupo, LugarDesarrollo, Periodo, MetodoEvaluacion, CursoRac
from .serializers import (
    ProgramaSerializer, CursoSerializer, RapSerializer, RacSerializer,
    ModalidadSerializer, CorteSerializer, GrupoSerializer,
    LugarDesarrolloSerializer, PeriodoSerializer, MetodoEvaluacionSerializer
)
from .filters import CursoFilter, RacFilter


class ProgramaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programa.objects.select_related('facultad', 'modalidad').all()
    serializer_class = ProgramaSerializer


class CursoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Curso.objects.select_related('programa').all()
    serializer_class = CursoSerializer
    filterset_class = CursoFilter

    @action(detail=True, methods=['get'], url_path='racs')
    def racs(self, request, pk=None):
        """Devuelve los RAC asociados a este curso via la matriz curricular curso_rac."""
        curso = self.get_object()
        rac_ids = CursoRac.objects.filter(curso=curso).values_list('rac_id', flat=True)
        racs = Rac.objects.filter(id__in=rac_ids).select_related('rap')
        serializer = RacSerializer(racs, many=True)
        return Response(serializer.data)


class RapViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rap.objects.all()
    serializer_class = RapSerializer


class RacViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rac.objects.select_related('rap').all()
    serializer_class = RacSerializer
    filterset_class = RacFilter


class ModalidadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer


class CorteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Corte.objects.all()
    serializer_class = CorteSerializer


class GrupoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer


class LugarDesarrolloViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LugarDesarrollo.objects.all()
    serializer_class = LugarDesarrolloSerializer


class PeriodoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer


class MetodoEvaluacionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetodoEvaluacion.objects.all()
    serializer_class = MetodoEvaluacionSerializer
    