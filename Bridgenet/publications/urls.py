from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.PublicacionListView.as_view(), name='lista'),
    path('nueva/', views.PublicacionCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.PublicacionDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.PublicacionUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.PublicacionDeleteView.as_view(), name='eliminar'),
    path('<int:pk>/comentar/', views.agregar_comentario, name='agregar_comentario'),
]
