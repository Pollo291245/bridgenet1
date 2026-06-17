from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Empresa, MiembroEmpresa, ValoracionEmpresa
from .models import Empresa, MiembroEmpresa
from .forms import EmpresaForm
from products.models import Producto
from publications.models import Publicacion
from users.models import User
from .forms import EmpresaUpdateForm
from .forms import EmpresaForm, AgregarMiembroForm
from django.db import transaction

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
        if hasattr(Empresa, 'tamano_choices'):
            context['tamanos'] = Empresa.tamano_choices.choices
        context['query_actual'] = self.request.GET.get('q', '')
        context['tamano_actual'] = self.request.GET.get('tamano', '')
        context['area_actual'] = self.request.GET.get('area', '')
        return context


class EmpresaDetailView(DetailView):
    model = Empresa
    template_name = 'enterprises/detalle_empresa.html'
    context_object_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = False
        if self.request.user.is_authenticated:
            context['es_admin'] = MiembroEmpresa.objects.filter(
                empresa=self.object,
                usuario=self.request.user,
                rol=MiembroEmpresa.rol_choices.ADMIN
            ).exists()
        return context


class EmpresaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'enterprises/empresa_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Los datos de la empresa se actualizaron correctamente.')
        return reverse('enterprises:detalle', kwargs={'pk': self.object.pk})

    def test_func(self):
        empresa = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=empresa, 
            usuario=self.request.user, 
            rol=MiembroEmpresa.rol_choices.ADMIN
        ).exists()



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

@login_required
def valorar_empresa(request, pk):
    empresa_objetivo = get_object_or_404(Empresa, pk=pk)
    
    if request.method == 'POST':
        membresia_usuario = request.user.empresas_miembro.first()
        if not membresia_usuario:
            messages.error(request, "No perteneces a ninguna empresa para realizar valoraciones.")
            return redirect('enterprises:detalle', pk=pk)
        mi_empresa = membresia_usuario.empresa

        if mi_empresa == empresa_objetivo:
            messages.error(request, "No puedes valorar a tu propia empresa.")
            return redirect('enterprises:detalle', pk=pk)

        try:
            puntuacion = int(request.POST.get('puntuacion'))
        except (TypeError, ValueError):
            messages.error(request, "El valor de la calificación no es válido.")
            return redirect('enterprises:detalle', pk=pk)

        if puntuacion < 1 or puntuacion > 5:
            messages.error(request, "La valoración debe estar entre 1 y 5.")
            return redirect('enterprises:detalle', pk=pk)
            
        ValoracionEmpresa.objects.update_or_create(
            autor=mi_empresa,
            empresa_evaluada=empresa_objetivo,
            defaults={'valoracion': puntuacion}
        )
        
        messages.success(request, '¡Gracias por calificar a esta empresa!')
        
    return redirect('enterprises:detalle', pk=pk)



class PanelAdministracionView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Empresa
    template_name = 'enterprises/panel_admin.html'
    context_object_name = 'empresa'

    def test_func(self):
        empresa = self.get_object()
        return MiembroEmpresa.objects.filter(
            empresa=empresa, 
            usuario=self.request.user, 
            rol=MiembroEmpresa.rol_choices.ADMIN
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_object()

        context['total_usuarios'] = empresa.miembros_empresa.count()
        context['total_publicaciones'] = empresa.publicaciones.count()
        context['total_productos'] = empresa.productos.count()
        context['total_valoraciones_recibidas'] = empresa.valoraciones_recibidas.count()
        context['veces_marcada_favorita'] = empresa.empresa_favorita_rel.count() 
        
        context['ultimos_usuarios'] = empresa.miembros_empresa.all().order_by('-created_at')[:5]

        return context
    
@login_required
def agregar_usuario(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    
    # BARRERA DE SEGURIDAD: Comprobar que el usuario activo sea ADMIN de esta empresa
    es_admin = MiembroEmpresa.objects.filter(
        empresa=empresa, 
        usuario=request.user, 
        rol=MiembroEmpresa.rol_choices.ADMIN
    ).exists()
    
    if not es_admin:
        messages.error(request, "Acceso denegado: Solo los administradores pueden invitar miembros.")
        return redirect('enterprises:detalle', pk=pk)

    if request.method == 'POST':
        form = AgregarMiembroForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Creamos el usuario base (contraseña ya encriptada)
                    nuevo_usuario = form.save()
                    
                    # 2. Lo vinculamos a la empresa actual
                    MiembroEmpresa.objects.create(
                        empresa=empresa,
                        usuario=nuevo_usuario,
                        rol=form.cleaned_data['rol'],
                        es_responsable_chat=form.cleaned_data['es_responsable_chat'],
                        is_active=True
                    )
                messages.success(request, f"El usuario {nuevo_usuario.username} fue agregado a la empresa con éxito.")
                return redirect('enterprises:panel_admin', pk=pk)
            except Exception as e:
                messages.error(request, f"Ocurrió un error al vincular el usuario: {str(e)}")
    else:
        form = AgregarMiembroForm()

    return render(request, 'enterprises/agregar_usuario.html', {'form': form, 'empresa': empresa})

class EmpresaNovedadesListView(DetailView):
    model = Empresa
    template_name = 'enterprises/empresa_novedades.html'
    context_object_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Novedades de esta empresa
        context['novedades'] = self.object.publicaciones.all().order_by('-fecha_publicacion')
        
        # Seguridad visual para el botón "Crear Novedad"
        context['puede_editar'] = False
        if self.request.user.is_authenticated:
            context['puede_editar'] = MiembroEmpresa.objects.filter(
                empresa=self.object,
                usuario=self.request.user,
                rol__in=[MiembroEmpresa.rol_choices.ADMIN, MiembroEmpresa.rol_choices.EDITOR]
            ).exists()
            
        return context
    
def editar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    
    
    if request.method == 'POST':
        form = EmpresaUpdateForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil de empresa actualizado con éxito.')
            return redirect('enterprises:detalle', pk=empresa.pk)
    else:
        form = EmpresaUpdateForm(instance=empresa)
        
    return render(request, 'enterprises/empresa_form.html', {'form': form, 'empresa': empresa})