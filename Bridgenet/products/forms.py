from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Excluimos 'empresa' porque el sistema lo asignará automáticamente
        fields = ['nombre_producto', 'imagen', 'descripcion_producto', 'precio', 'cantidad_minima_pedido', 'categoria', 'unidad_medida', 'stock_disponible']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion_producto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidad_minima_pedido': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
        }