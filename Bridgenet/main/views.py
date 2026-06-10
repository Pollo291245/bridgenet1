from django.shortcuts import render

from products.models import Producto
from enterprises.models import Enterprise

def inicio(request):
    productos_aleatorios = Producto.objects.all().order_by('?')[:12]
    empresas_aleatorias = Enterprise.objects.all().order_by('?')[:12]

    context = {
        'productos': productos_aleatorios,
        'empresas': empresas_aleatorias
    }

    return render(request, 'inicio.html', context)
