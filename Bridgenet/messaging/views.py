from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Conversacion, Mensaje
from enterprises.models import Empresa, MiembroEmpresa
from django.urls import reverse
from products.models import Producto

def obtener_mi_empresa(usuario):
    """Función de ayuda para obtener la empresa del usuario actual"""
    membresia = usuario.empresas_miembro.first()
    return membresia.empresa if membresia else None

@login_required
def bandeja_entrada(request):
    mi_empresa = obtener_mi_empresa(request.user)
    if not mi_empresa:
        messages.error(request, "No perteneces a ninguna empresa.")
        return redirect('inicio')

    # Obtenemos todas las conversaciones donde participa mi empresa
    conversaciones = Conversacion.objects.filter(
        Q(empresa_solicitante=mi_empresa) | Q(empresa_receptora=mi_empresa)
    ).order_by('-actualizado_en')

    return render(request, 'messaging/bandeja_entrada.html', {
        'conversaciones': conversaciones,
        'mi_empresa': mi_empresa
    })



@login_required
def iniciar_conversacion(request, empresa_id):
    mi_empresa = obtener_mi_empresa(request.user)
    empresa_destino = get_object_or_404(Empresa, id=empresa_id)

    if mi_empresa == empresa_destino:
        messages.warning(request, "No puedes chatear con tu propia empresa.")
        return redirect('enterprises:detalle', pk=empresa_id)

    conversacion = Conversacion.objects.filter(
        Q(empresa_solicitante=mi_empresa, empresa_receptora=empresa_destino) |
        Q(empresa_solicitante=empresa_destino, empresa_receptora=mi_empresa)
    ).first()

    if not conversacion:
        conversacion = Conversacion.objects.create(
            empresa_solicitante=mi_empresa,
            empresa_receptora=empresa_destino
        )

    # NUEVO: Si viene un producto_id en la URL, lo pasamos a la sala de chat
    url_destino = reverse('messaging:detalle_conversacion', kwargs={'conversacion_id': conversacion.id})
    producto_id = request.GET.get('producto_id')
    
    if producto_id:
        url_destino += f"?producto_id={producto_id}"
        
    return redirect(url_destino)

@login_required
def detalle_conversacion(request, conversacion_id):
    mi_empresa = obtener_mi_empresa(request.user)
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)

    if mi_empresa not in [conversacion.empresa_solicitante, conversacion.empresa_receptora]:
        messages.error(request, "No tienes permiso para ver esta conversación.")
        return redirect('messaging:bandeja_entrada')

    membresia = MiembroEmpresa.objects.get(usuario=request.user, empresa=mi_empresa)
    if not membresia.es_responsable_chat:
        messages.error(request, "No tienes permisos de chat en tu empresa.")
        return redirect('messaging:bandeja_entrada')

    Mensaje.objects.filter(conversacion=conversacion).exclude(empresa_remitente=mi_empresa).update(leido=True)

    # NUEVO: Lógica para detectar si venimos desde un producto
    producto_id = request.GET.get('producto_id')
    mensaje_predefinido = ""
    producto_contexto = None

    if producto_id:
        try:
            producto_contexto = Producto.objects.get(id=producto_id)
            mensaje_predefinido = f"Hola, nos interesa obtener más información sobre el producto: {producto_contexto.nombre_producto}."
        except Producto.DoesNotExist:
            pass

    # Lógica de guardado de mensajes (se mantiene igual)
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            Mensaje.objects.create(
                conversacion=conversacion,
                autor=request.user,
                empresa_remitente=mi_empresa,
                contenido=contenido
            )
            conversacion.save() 
            return redirect('messaging:detalle_conversacion', conversacion_id=conversacion.id)

    mensajes = conversacion.mensajes.all()
    otra_empresa = conversacion.get_otra_empresa(mi_empresa)

    # NUEVO: Agregamos las variables del producto al contexto
    return render(request, 'messaging/detalle_conversacion.html', {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'mi_empresa': mi_empresa,
        'otra_empresa': otra_empresa,
        'producto_contexto': producto_contexto,
        'mensaje_predefinido': mensaje_predefinido
    })