from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OfertaAcademicaViewSet, MatriculadosPorOfertaView, RubricaCriterioViewSet,
    EvaluacionRacViewSet, EstadisticaEvaluacionView, DiligenciarEvaluacionRacView,
    ImportarEstudiantesExcelView
)

router = DefaultRouter()
router.register(r'ofertas', OfertaAcademicaViewSet, basename='oferta')
router.register(r'rubrica-criterios', RubricaCriterioViewSet, basename='rubrica-criterio')
router.register(r'evaluaciones-rac', EvaluacionRacViewSet, basename='evaluacion-rac')

urlpatterns = [
    path('ofertas/<int:oferta_id>/matriculados/', MatriculadosPorOfertaView.as_view(), name='oferta-matriculados'),
    path('evaluaciones-rac/diligenciar/', DiligenciarEvaluacionRacView.as_view(), name='evaluacion-rac-diligenciar'),
    path('evaluaciones-rac/<int:evaluacion_id>/estadisticas/', EstadisticaEvaluacionView.as_view(), name='evaluacion-rac-estadisticas'),
    path('', include(router.urls)),
        path('matricula/importar-excel/', ImportarEstudiantesExcelView.as_view(), name='matricula-importar-excel'),
]