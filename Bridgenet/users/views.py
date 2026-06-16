from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect, render

from enterprises.models import Empresa, MiembroEmpresa

from .forms import EmpresaRegistroForm, PerfilForm, AuthenticationForm



class InicioSesionView(LoginView):
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True


class CerrarSesionView(LogoutView):
    next_page = 'inicio'


def registro(request):
    if request.user.is_authenticated:
        return redirect('perfil')

    if request.method == 'POST':
        form = EmpresaRegistroForm(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            email_usuario = form.cleaned_data['email']
            
            with transaction.atomic():
                empresa = Empresa.objects.create(
                    rut=form.cleaned_data['rut'],
                    nombre=form.cleaned_data['nombre'],
                    area_produccion=form.cleaned_data['area_produccion'],
                    email=form.cleaned_data['email_empresa'],
                    direccion=form.cleaned_data['direccion'],
                    sitio_web=form.cleaned_data['sitio_web'],
                    telefono=form.cleaned_data['telefono'],
                )
                
                user = UserModel.objects.create_user(
                    username=email_usuario, 
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=email_usuario, # Usamos el email aquí también
                    password=form.cleaned_data['password1'],
                )
                
                MiembroEmpresa.objects.create(
                    empresa=empresa, 
                    usuario=user, 
                    rol=MiembroEmpresa.rol_choices.ADMIN,
                    es_responsable_chat=True 
                )

            messages.success(request, 'La empresa y su usuario administrador fueron creados correctamente. Ahora puedes iniciar sesión con tu correo.')
            return redirect('login')
    else:
        form = EmpresaRegistroForm()

    return render(request, 'users/registro.html', {'form': form})


@login_required
def perfil(request):
    membresia = request.user.empresas_miembro.select_related('empresa').first()
    empresa = membresia.empresa if membresia else None
    
    return render(request, 'users/perfil.html', {
        'usuario': request.user,
        'empresa': empresa,
        'membresia': membresia,
    })


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil fue actualizado correctamente.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)

    return render(request, 'users/perfil_form.html', {'form': form})
