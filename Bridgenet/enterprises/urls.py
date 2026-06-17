from django.urls import path
from . import views

app_name = 'enterprises'

urlpatterns = [
    path('', views.EmpresaListView.as_view(), name='lista'),
    path('<int:pk>/', views.EmpresaDetailView.as_view(), name='detalle'),
    path('<int:pk>/panel/', views.PanelAdministracionView.as_view(), name='panel_admin'),
    path('<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='editar'),
    path('<int:pk>/valorar/', views.valorar_empresa, name='valorar'),
    path('<int:pk>/invitar/', views.agregar_usuario, name='agregar_usuario'),
    path('<int:pk>/novedades/', views.EmpresaNovedadesListView.as_view(), name='novedades'),
    path('<int:pk>/seguir/', views.toggle_seguir_empresa, name='seguir_empresa'),
]