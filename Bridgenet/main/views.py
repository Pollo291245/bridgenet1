from django.shortcuts import render

from enterprises.models import Empresa
from products.models import Producto
from publications.models import Publicacion

def inicio(request):
    ultimas_publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')[:12]
    productos_aleatorios = Producto.objects.all().order_by('?')[:12]
    empresas_aleatorias = Empresa.objects.all().order_by('?')[:12]

    total_empresas_activas = Empresa.objects.filter(estado=Empresa.estado_choices.ACTIVO).count()
    total_productos = Producto.objects.all().count()

    context = {
        'publicaciones': ultimas_publicaciones,
        'productos': productos_aleatorios,
        'empresas': empresas_aleatorias,
        # Pasamos los totales al contexto
        'total_empresas': total_empresas_activas,
        'total_productos': total_productos,
    }

    return render(request, 'inicio.html', context)