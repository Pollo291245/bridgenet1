from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .forms import ComentarioForm
from .models import Publicacion, Comentarios
from enterprises.models import MiembroEmpresa

# 1. Listado general de publicaciones
class PublicacionListView(ListView):
    model = Publicacion
    template_name = 'publications/lista_publicaciones.html'
    context_object_name = 'publicaciones'
    ordering = ['-fecha_publicacion'] # Las más recientes primero

# 2. Detalle de una publicación
class PublicacionDetailView(DetailView):
    model = Publicacion
    template_name = 'publications/detalle_publicacion.html'
    context_object_name = 'publicacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ESTA ES LA CLAVE PARA EL FRONTEND: 
        # Le enviamos al HTML un aviso de si este usuario tiene permiso para ver los botones
        context['puede_editar'] = False
        if self.request.user.is_authenticated:
            context['puede_editar'] = MiembroEmpresa.objects.filter(
                empresa=self.object.empresa,
                usuario=self.request.user,
                rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
            ).exists()
        return context

# 3. Crear Publicación (Solo Admin y Editor)
class PublicacionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Publicacion
    template_name = 'publications/publicacion_form.html'
    fields = ['titulo', 'contenido', 'imagen', 'tipo_novedad', 'producto_referido']

    def test_func(self):
        # ¿Tiene el usuario un rol que le permita crear?
        membresia = self.request.user.empresas_miembro.first()
        if not membresia: return False
        return membresia.rol in [MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]

    def form_valid(self, form):
        # Asignamos la empresa automáticamente
        membresia = self.request.user.empresas_miembro.first()
        form.instance.empresa = membresia.empresa
        messages.success(self.request, 'Publicación creada con éxito.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('publications:detalle', kwargs={'pk': self.object.pk})

# 4. Editar Publicación (Solo Admin y Editor de la misma empresa)
class PublicacionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publicacion
    template_name = 'publications/publicacion_form.html'
    fields = ['titulo', 'contenido', 'imagen', 'tipo_novedad', 'producto_referido']

    def test_func(self):
        publicacion = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=publicacion.empresa,
            usuario=self.request.user,
            rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
        ).exists()

    def get_success_url(self):
        messages.success(self.request, 'Publicación actualizada correctamente.')
        return reverse('publications:detalle', kwargs={'pk': self.object.pk})

# 5. Eliminar Publicación (Solo Admin y Editor de la misma empresa)
# Asegúrate de importar el formulario arriba:
# from .forms import ComentarioForm

class PublicacionDetailView(DetailView):
    model = Publicacion
    template_name = 'publications/detalle_publicacion.html'
    context_object_name = 'publicacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Lógica de seguridad visual que ya teníamos
        context['puede_editar'] = False
        if self.request.user.is_authenticated:
            context['puede_editar'] = MiembroEmpresa.objects.filter(
                empresa=self.object.empresa,
                usuario=self.request.user,
                rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
            ).exists()
            
        # 2. NUEVO: Enviar comentarios y el formulario vacío al HTML
        # Filtramos los comentarios asociados a esta publicación y los ordenamos por fecha (más recientes primero)
        context['comentarios'] = self.object.comentarios_publicacion.all().order_by('-fecha_comentario')
        context['comentario_form'] = ComentarioForm()
        
        return context
    
from django.contrib.auth.decorators import login_required

@login_required
def agregar_comentario(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    
    if request.method == 'POST':
        membresia = request.user.empresas_miembro.first()
        
        # Validamos que el usuario pertenezca a una empresa para poder comentar
        if not membresia:
            messages.error(request, "Debes pertenecer a una empresa para comentar.")
            return redirect('publications:detalle', pk=pk)
            
        form = ComentarioForm(request.POST)
        if form.is_valid():
            # No guardamos directamente, porque nos falta asignarle el autor y la publicación
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.autor = membresia.empresa
            nuevo_comentario.publicacion = publicacion
            nuevo_comentario.save()
            
            messages.success(request, "Tu comentario ha sido publicado.")
            
    return redirect('publications:detalle', pk=pk)



class PublicacionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Publicacion
    template_name = 'publications/publicacion_confirm_delete.html'
    success_url = reverse_lazy('publications:lista')

    def test_func(self):
        publicacion = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=publicacion.empresa,
            usuario=self.request.user,
            rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
        ).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Publicación eliminada correctamente.')
        return super().delete(request, *args, **kwargs)