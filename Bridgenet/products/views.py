from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
from .models import Producto, ValoracionProducto
from .forms import ProductoForm

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
            # Busca coincidencias en el nombre o en la descripción
            queryset = queryset.filter(Q(nombre_producto__icontains=q) | Q(descripcion_producto__icontains=q))
        if categoria:
            queryset = queryset.filter(categoria=categoria)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos las categorías al HTML para el selector de filtros
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

# 3. Edición de producto (/productos/<id>/editar/)
class ProductoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html'

    def get_success_url(self):
        messages.success(self.request, 'El producto se actualizó correctamente.')
        return reverse('products:detalle', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Seguridad: Solo puede editar quien pertenezca a la empresa dueña del producto
        producto = self.get_object()
        return self.request.user.is_authenticated and self.request.user.empresa_rel == producto.empresa

# 4. Guardar producto como favorito (/productos/<id>/guardar/)
@login_required
def toggle_guardar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    user = request.user
    
    if user.productos_guardados.filter(pk=pk).exists():
        user.productos_guardados.remove(producto)
        messages.info(request, f'Quitaste {producto.nombre_producto} de tu lista de guardados.')
    else:
        user.productos_guardados.add(producto)
        messages.success(request, f'Añadiste {producto.nombre_producto} a tu lista de guardados.')
        
    return redirect('products:detalle', pk=pk)

# 5. Valorar producto (/productos/<id>/valorar/)
@login_required
def valorar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '')
        
        # Verificamos que el usuario tenga una empresa asociada para poder ser "autor"
        if request.user.empresa_rel:
            ValoracionProducto.objects.update_or_create(
                autor=request.user.empresa_rel, 
                producto_evaluado=producto,
                defaults={'valoracion': puntuacion, 'comentario': comentario}
            )
            messages.success(request, '¡Gracias por calificar este producto!')
        else:
            messages.error(request, 'Necesitas registrar o asociar una empresa a tu perfil para dejar valoraciones B2B.')
            
    return redirect('products:detalle', pk=pk)

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html' # Reutilizamos el mismo HTML de edición

    def form_valid(self, form):
        # Antes de guardar, le asignamos automáticamente la empresa del usuario
        if not self.request.user.empresa_rel:
            messages.error(self.request, "Debes tener una empresa asociada para crear productos.")
            return redirect('perfil')
            
        form.instance.empresa = self.request.user.empresa_rel
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
        # Seguridad: Solo puede eliminar quien pertenezca a la empresa dueña del producto
        producto = self.get_object()
        return self.request.user.is_authenticated and self.request.user.empresa_rel == producto.empresa

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Producto eliminado correctamente.')
        return super().delete(request, *args, **kwargs)