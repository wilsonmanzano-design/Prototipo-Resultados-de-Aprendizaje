from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ObtenerCsrfView, LoginView, LogoutView, MeView, SoloAdminPingView,
    ProgramaViewSet, CursoViewSet, RapViewSet, RacViewSet, ModalidadViewSet,
    CorteViewSet, GrupoViewSet, LugarDesarrolloViewSet, PeriodoViewSet,
    MetodoEvaluacionViewSet
)

router = DefaultRouter()
router.register(r'programas', ProgramaViewSet, basename='programa')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'raps', RapViewSet, basename='rap')
router.register(r'racs', RacViewSet, basename='rac')
router.register(r'modalidades', ModalidadViewSet, basename='modalidad')
router.register(r'cortes', CorteViewSet, basename='corte')
router.register(r'grupos', GrupoViewSet, basename='grupo')
router.register(r'lugares-desarrollo', LugarDesarrolloViewSet, basename='lugar-desarrollo')
router.register(r'periodos', PeriodoViewSet, basename='periodo')
router.register(r'metodos-evaluacion', MetodoEvaluacionViewSet, basename='metodo-evaluacion')

urlpatterns = [
    path('auth/csrf/', ObtenerCsrfView.as_view(), name='auth-csrf'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/solo-admin-ping/', SoloAdminPingView.as_view(), name='auth-solo-admin-ping'),
    path('', include(router.urls)),
]