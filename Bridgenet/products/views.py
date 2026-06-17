from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Producto, ValoracionProducto
from .forms import ProductoForm
from enterprises.models import MiembroEmpresa  # <-- IMPORTANTE: Importamos MiembroEmpresa

# 1. Listado de productos con filtros (/productos/)
class ProductoListView(ListView):
    model = Producto
    template_name = 'products/lista_productos.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        q = self.request.GET.get('q', '')
        categoria = self.request.GET.get('categoria', '')

        if q:
            queryset = queryset.filter(Q(nombre_producto__icontains=q) | Q(descripcion_producto__icontains=q))
        if categoria:
            queryset = queryset.filter(categoria=categoria)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(Producto, 'CategoriaChoices'):
            context['categorias'] = Producto.CategoriaChoices.choices
        context['query_actual'] = self.request.GET.get('q', '')
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        return context

# 2. Detalle del producto (/productos/<id>/)
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'products/detalle_producto.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Enviamos la variable al HTML para ocultar/mostrar botones
        context['puede_editar'] = False
        if self.request.user.is_authenticated:
            context['puede_editar'] = MiembroEmpresa.objects.filter(
                empresa=self.object.empresa,
                usuario=self.request.user,
                rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
            ).exists()
        return context

# 3. Edición de producto (/productos/<id>/editar/)
class ProductoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html'

    def get_success_url(self):
        messages.success(self.request, 'El producto se actualizó correctamente.')
        return reverse('products:detalle', kwargs={'pk': self.object.pk})

    def test_func(self):
        # SEGURIDAD POR ROLES: Solo Admin o Editor de la empresa dueña del producto
        producto = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=producto.empresa,
            usuario=self.request.user,
            rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
        ).exists()

# 4. Guardar producto como favorito (/productos/<id>/guardar/)
@login_required
def toggle_seguir_empresa(request, pk):
    empresa_objetivo = get_object_or_404(Empresa, pk=pk)
    usuario = request.user

    # Opcional: Evitar que el usuario siga a su propia empresa
    membresia = usuario.empresas_miembro.first()
    if membresia and membresia.empresa == empresa_objetivo:
        messages.warning(request, "No puedes seguir a tu propia empresa.")
        # Redirigimos de vuelta
        ruta_anterior = request.META.get('HTTP_REFERER')
        return redirect(ruta_anterior if ruta_anterior else 'enterprises:detalle', pk=pk)

    # Lógica de Seguir / Dejar de seguir vinculada al USUARIO
    if empresa_objetivo in usuario.proveedores_favoritos.all():
        usuario.proveedores_favoritos.remove(empresa_objetivo)
        messages.info(request, f'Has dejado de seguir a {empresa_objetivo.nombre}.')
    else:
        usuario.proveedores_favoritos.add(empresa_objetivo)
        messages.success(request, f'Ahora sigues a {empresa_objetivo.nombre}.')
        
    # Redirige de vuelta a la misma página
    ruta_anterior = request.META.get('HTTP_REFERER')
    if ruta_anterior:
        return redirect(ruta_anterior)
    return redirect('enterprises:detalle', pk=pk)

# 5. Valorar producto (/productos/<id>/valorar/)
@login_required
def valorar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '')
        
        # 1. Obtener la empresa del usuario
        membresia = request.user.empresas_miembro.first()
        
        if membresia:
            mi_empresa = membresia.empresa
            
            # 2. Evitar que una empresa se valore a sí misma a través de sus productos
            if mi_empresa == producto.empresa:
                messages.error(request, "No puedes valorar los productos de tu propia empresa.")
            else:
                ValoracionProducto.objects.update_or_create(
                    autor=mi_empresa, 
                    producto_evaluado=producto,
                    defaults={'valoracion': puntuacion, 'comentario': comentario}
                )
                messages.success(request, '¡Gracias por calificar este producto!')
        else:
            messages.error(request, 'Necesitas pertenecer a una empresa para dejar valoraciones B2B.')
            
    return redirect('products:detalle', pk=pk)

# C: Crear Producto (/productos/nuevo/)
class ProductoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html'

    def test_func(self):
        # SEGURIDAD POR ROLES: Para crear un producto, debes ser Admin o Editor
        membresia = self.request.user.empresas_miembro.first()
        if not membresia:
            return False
        return membresia.rol in [MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]

    def form_valid(self, form):
        membresia = self.request.user.empresas_miembro.first()
        form.instance.empresa = membresia.empresa
        messages.success(self.request, '¡Producto creado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('products:detalle', kwargs={'pk': self.object.pk})

# D: Eliminar Producto (/productos/<id>/eliminar/)
class ProductoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Producto
    template_name = 'products/producto_confirm_delete.html'
    success_url = reverse_lazy('products:lista')

    def test_func(self):
        # SEGURIDAD POR ROLES: Solo Admin o Editor pueden eliminar. 
        # (Si quisieras ser más estricto, podrías dejar solo a ADMIN aquí quitando a EDITOR de la lista)
        producto = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=producto.empresa,
            usuario=self.request.user,
            rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
        ).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Producto eliminado correctamente.')
        return super().delete(request, *args, **kwargs)