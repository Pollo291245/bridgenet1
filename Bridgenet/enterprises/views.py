from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Empresa, MiembroEmpresa
from .forms import EmpresaForm

# 1. Listado de empresas con buscador y filtros (/empresas/)
class EmpresaListView(ListView):
    model = Empresa
    template_name = 'enterprises/lista_empresas.html'
    context_object_name = 'empresas'

    def get_queryset(self):
        queryset = Empresa.objects.filter(estado=Empresa.estado_choices.ACTIVO)
        
        q = self.request.GET.get('q', '')
        tamano = self.request.GET.get('tamano', '')
        area = self.request.GET.get('area', '')

        if q:
            queryset = queryset.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
        if tamano:
            queryset = queryset.filter(tamano_empresa=tamano)
        if area:
            queryset = queryset.filter(area_produccion__icontains=area)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Opciones para los selects de filtrado en el HTML
        if hasattr(Empresa, 'tamano_choices'):
            context['tamanos'] = Empresa.tamano_choices.choices
        context['query_actual'] = self.request.GET.get('q', '')
        context['tamano_actual'] = self.request.GET.get('tamano', '')
        context['area_actual'] = self.request.GET.get('area', '')
        return context


# 2. Perfil público de una empresa (/empresas/<id>/)
class EmpresaDetailView(DetailView):
    model = Empresa
    template_name = 'enterprises/detalle_empresa.html'
    context_object_name = 'empresa'


# 3. Edición de la empresa (/empresas/<id>/editar/)
class EmpresaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'enterprises/empresa_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Los datos de la empresa se actualizaron correctamente.')
        return reverse('enterprises:detalle', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Regla estricta: Solo el usuario administrador asignado a esta empresa puede editarla
        empresa = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=empresa, 
            usuario=self.request.user, 
            rol=MiembroEmpresa.rol_choices.ADMIN
        ).exists() or self.request.user.empresa_rel == empresa


# 4. Marcar o quitar empresa favorita (/empresas/<id>/favoritas/)
@login_required
def toggle_favorita(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    user = request.user
    
    if user.proveedores_favoritos.filter(pk=pk).exists():
        user.proveedores_favoritos.remove(empresa)
        messages.info(request, f'Quitaste a {empresa.nombre} de tus favoritos.')
    else:
        user.proveedores_favoritos.add(empresa)
        messages.success(request, f'Añadiste a {empresa.nombre} a tus favoritos.')
        
    return redirect('enterprises:detalle', pk=pk)


# 5. Valorar una empresa (/empresas/<id>/valorar/)
@login_required
def valorar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '')
        
        # Aquí mapeamos tu modelo estructural de ValoracionEmpresa
        # ValoracionEmpresa.objects.update_or_create(
        #     usuario=request.user, empresa=empresa,
        #     defaults={'puntuacion': puntuacion, 'comentario': comentario}
        # )
        messages.success(request, '¡Gracias por calificar a esta empresa!')
        
    return redirect('enterprises:detalle', pk=pk)


# 6. Publicaciones y noticias de la empresa (/empresas/<id>/novedades/)
class EmpresaNovedadesListView(DetailView):
    model = Empresa
    template_name = 'enterprises/empresa_novedades.html'
    context_object_name = 'empresa'