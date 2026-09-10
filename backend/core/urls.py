from django.urls import path
from .views import ObtenerCsrfView, LoginView, LogoutView, MeView, SoloAdminPingView

urlpatterns = [
    path('auth/csrf/', ObtenerCsrfView.as_view(), name='auth-csrf'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/solo-admin-ping/', SoloAdminPingView.as_view(), name='auth-solo-admin-ping'),
]