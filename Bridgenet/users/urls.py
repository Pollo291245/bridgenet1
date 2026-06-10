from django.urls import path

from .views import CerrarSesionView, InicioSesionView, editar_perfil, perfil, registro

urlpatterns = [
    path('login/', InicioSesionView.as_view(), name='login'),
    path('logout/', CerrarSesionView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),
    path('perfil/', perfil, name='perfil'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
]