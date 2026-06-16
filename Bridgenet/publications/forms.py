from django import forms
from .models import Comentarios

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentarios
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Escribe un comentario o consulta sobre esta publicación...'
            }),
        }
        labels = {
            'comentario': ''
        }