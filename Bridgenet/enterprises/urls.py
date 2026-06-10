from django.urls import path
from . import views

app_name = 'enterprises'

urlpatterns = [
    path('', views.EmpresaListView.as_view(), name='lista'),
    path('<int:pk>/', views.EmpresaDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='editar'),
    path('<int:pk>/favoritas/', views.toggle_favorita, name='toggle_favorita'),
    path('<int:pk>/valorar/', views.valorar_empresa, name='valorar'),
    path('<int:pk>/novedades/', views.EmpresaNovedadesListView.as_view(), name='novedades'),
]