from django.shortcuts import render

from enterprises.models import Empresa
from products.models import Producto

def inicio(request):
    productos_aleatorios = Producto.objects.all().order_by('?')[:12]
    empresas_aleatorias = Empresa.objects.all().order_by('?')[:12]

    context = {
        'productos': productos_aleatorios,
        'empresas': empresas_aleatorias
    }

    return render(request, 'inicio.html', context)
