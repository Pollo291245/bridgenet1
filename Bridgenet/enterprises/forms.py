from django import forms
from .models import Empresa

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        # Campos editables de la empresa
        fields = ['nombre', 'area_produccion', 'email', 'direccion', 'sitio_web', 'telefono']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area_produccion': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        