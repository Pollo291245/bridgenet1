from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Empresa
from .models import Empresa, MiembroEmpresa

User = get_user_model()

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['rut', 'nombre', 'area_produccion', 'email', 'direccion', 'sitio_web', 'telefono']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area_produccion': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AdminUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AgregarMiembroForm(UserCreationForm):
    rol = forms.ChoiceField(
        choices=MiembroEmpresa.rol_choices.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    es_responsable_chat = forms.BooleanField(
        required=False,
        label="¿Asignar como responsable del chat de la empresa?",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
        # Ya no necesitamos definir los widgets aquí porque lo haremos en el __init__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iteramos sobre todos los campos del formulario generados por Django
        for field_name, field in self.fields.items():
            # Excluimos el checkbox (que usa form-check-input) y el selector (form-select)
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.Select):
                # Le asignamos la clase form-control a todo el resto (textos, correos y contraseñas)
                field.widget.attrs['class'] = 'form-control'
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EmpresaUpdateForm(forms.ModelForm):
    sitio_web = forms.CharField(
        required=False,
        label="Sitio Web (opcional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo.com'})
    )

    class Meta:
        model = Empresa
        fields = ['nombre', 'logo', 'area_produccion', 'email', 'direccion', 'sitio_web', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'area_produccion': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_sitio_web(self):
        url = self.cleaned_data.get('sitio_web')
        if url:
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
        return url