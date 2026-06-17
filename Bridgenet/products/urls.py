from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista'),
    path('crear/', views.ProductoCreateView.as_view(), name='crear'), # <-- NUEVA
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='eliminar'), # <-- NUEVA
    path('<int:pk>/seguir/', views.toggle_seguir_empresa, name='seguir_empresa'),
    path('<int:pk>/valorar/', views.valorar_producto, name='valorar'),
    
]