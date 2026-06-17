from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.bandeja_entrada, name='bandeja_entrada'),
    path('iniciar/<int:empresa_id>/', views.iniciar_conversacion, name='iniciar_conversacion'),
    path('chat/<int:conversacion_id>/', views.detalle_conversacion, name='detalle_conversacion'),
]