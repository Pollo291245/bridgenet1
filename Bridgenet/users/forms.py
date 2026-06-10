from django import forms

from enterprises.models import Empresa

from .models import User


class EmpresaRegistroForm(forms.Form):
    username = forms.CharField(label='Usuario administrador', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Nombre', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Apellido', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Correo del usuario', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    rut = forms.CharField(label='RUT', max_length=12, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label='Nombre de la empresa', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    area_produccion = forms.CharField(label='Área de producción', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email_empresa = forms.EmailField(label='Correo de la empresa', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label='Dirección', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sitio_web = forms.URLField(label='Sitio web', required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label='Teléfono', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ya existe un usuario con ese nombre.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con ese correo.')
        return email

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        if Empresa.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Ya existe una empresa con ese RUT.')
        return rut

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }