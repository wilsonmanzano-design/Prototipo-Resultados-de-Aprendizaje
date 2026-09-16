from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.permissions import EsAdministrador, EsDocenteDeLaOferta
from .models import OfertaAcademica, Matricula, EvaluacionRac, RubricaCriterio, VwEvaluacionEstadistica
from .serializers import (
    OfertaAcademicaSerializer, MatriculaSerializer, EvaluacionRacSerializer,
    RubricaCriterioSerializer, EstadisticaEvaluacionSerializer,
    DiligenciarEvaluacionRacSerializer
)
from rest_framework.parsers import MultiPartParser
from .services.importador_estudiantes import importar_estudiantes_desde_excel


class OfertaAcademicaViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista TODAS las ofertas si eres Administrador; solo las propias si eres Docente."""
    serializer_class = OfertaAcademicaSerializer

    def get_queryset(self):
        qs = OfertaAcademica.objects.select_related('curso', 'docente', 'periodo', 'modalidad', 'lugar_desarrollo')
        user = self.request.user
        if user.groups.filter(name='Administrador').exists():
            return qs
        if hasattr(user, 'docente'):
            return qs.filter(docente=user.docente)
        return qs.none()


class MatriculadosPorOfertaView(APIView):
    """GET /api/ofertas/<id>/matriculados/?corte=<id>
    Devuelve los estudiantes matriculados de una oferta en un corte especifico.
    Es la lista base para construir la tabla de la rubrica en el frontend (Fase 8)."""

    def get(self, request, oferta_id):
        oferta = get_object_or_404(OfertaAcademica, pk=oferta_id)
        self.check_object_permissions(request, oferta)
        corte_id = request.query_params.get('corte')
        if not corte_id:
            return Response({'detail': 'El parametro "corte" es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        matriculas = Matricula.objects.filter(
            oferta=oferta, corte_id=corte_id, estado='matriculado'
        ).select_related('estudiante')
        return Response(MatriculaSerializer(matriculas, many=True).data)

    def get_permissions(self):
        return [permissions.IsAuthenticated(), EsDocenteDeLaOferta()]

    def check_object_permissions(self, request, obj):
        for permiso in self.get_permissions():
            if isinstance(permiso, EsDocenteDeLaOferta) and not permiso.has_object_permission(request, self, obj):
                self.permission_denied(request, message=permiso.message)


class RubricaCriterioViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogo de criterios + sus 4 niveles anidados, para que el frontend pinte el formulario."""
    queryset = RubricaCriterio.objects.prefetch_related('niveles').all()
    serializer_class = RubricaCriterioSerializer


class EvaluacionRacViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EvaluacionRacSerializer
    filterset_fields = ['oferta', 'rac', 'corte']

    def get_queryset(self):
        qs = EvaluacionRac.objects.select_related('oferta', 'rac', 'corte')
        user = self.request.user
        if user.groups.filter(name='Administrador').exists():
            return qs
        if hasattr(user, 'docente'):
            return qs.filter(oferta__docente=user.docente)
        return qs.none()


class EstadisticaEvaluacionView(APIView):
    """GET /api/evaluaciones-rac/<id>/estadisticas/
    Expone la vista SQL vw_evaluacion_estadistica para una evaluacion puntual."""

    def get(self, request, evaluacion_id):
        evaluacion = get_object_or_404(EvaluacionRac, pk=evaluacion_id)
        estadistica = getattr(evaluacion, 'estadistica', None)
        if estadistica is None:
            return Response({'detail': 'Aun no hay datos de rubrica para esta evaluacion.'}, status=404)
        return Response(EstadisticaEvaluacionSerializer(estadistica).data)


class DiligenciarEvaluacionRacView(APIView):
    """POST /api/evaluaciones-rac/diligenciar/
    Endpoint central: guarda rubrica de todos los estudiantes + analisis, en una transaccion."""

    def post(self, request):
        serializer = DiligenciarEvaluacionRacSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        oferta = get_object_or_404(OfertaAcademica, pk=serializer.validated_data['oferta_id'])
        permiso = EsDocenteDeLaOferta()
        if not permiso.has_object_permission(request, self, oferta):
            return Response({'detail': permiso.message}, status=status.HTTP_403_FORBIDDEN)

        evaluacion = serializer.save()
        return Response(EvaluacionRacSerializer(evaluacion).data, status=status.HTTP_201_CREATED)

TAMANO_MAXIMO_MB = 5


class ImportarEstudiantesExcelView(APIView):
    """POST /api/matricula/importar-excel/
    Recibe multipart/form-data: archivo (.xlsx), oferta_id, corte_id."""

    parser_classes = [MultiPartParser]

    def post(self, request):
        archivo = request.FILES.get('archivo')
        oferta_id = request.data.get('oferta_id')
        corte_id = request.data.get('corte_id')

        if archivo is None:
            return Response({'detail': 'Debe adjuntar un archivo en el campo "archivo".'}, status=status.HTTP_400_BAD_REQUEST)
        if not archivo.name.lower().endswith('.xlsx'):
            return Response({'detail': 'El archivo debe tener extension .xlsx'}, status=status.HTTP_400_BAD_REQUEST)
        if archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024:
            return Response({'detail': f'El archivo supera el limite de {TAMANO_MAXIMO_MB} MB.'}, status=status.HTTP_400_BAD_REQUEST)
        if not oferta_id or not corte_id:
            return Response({'detail': 'Los campos "oferta_id" y "corte_id" son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

        oferta = get_object_or_404(OfertaAcademica, pk=oferta_id)
        permiso = EsDocenteDeLaOferta()
        if not permiso.has_object_permission(request, self, oferta):
            return Response({'detail': permiso.message}, status=status.HTTP_403_FORBIDDEN)

        resumen = importar_estudiantes_desde_excel(archivo, oferta_id=oferta.id, corte_id=corte_id)

        codigo_http = status.HTTP_200_OK if not resumen['errores'] else status.HTTP_207_MULTI_STATUS
        return Response(resumen, status=codigo_http)