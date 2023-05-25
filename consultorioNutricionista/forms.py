from datetime import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Patient, Consultation
from django.contrib.auth.models import User

# Esta clase define un formulario que será utilizado para la creación y edición de instancias de usuarios con el rol de nutricionista en el sistema.
# El formulario incluye campos para el email, username, nombres, apellidos, contraseña y confirmación de contraseña.
# La clase tiene un método clean que valida que las contraseñas coincidan y que tengan al menos 8 caracteres.

# El método clean es utilizado en los formularios de NutritionistForm y en los formularios que heredan de éste, como AssistantForm.
# El método se encarga de validar que las contraseñas ingresadas por el usuario coincidan y que tengan al menos 8 caracteres.
# Si la validación falla, el método lanzará una excepción que será capturada por Django y mostrará un mensaje de error al usuario.

class NutritionistForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    confirm_password = forms.CharField(widget=forms.PasswordInput, label=_('Confirm password'))

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'is_superuser')
        labels = {
            'email': _('Email'),
            'username': _('Username'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords don't match"))

        if password and len(password) < 8:
            raise forms.ValidationError(_('Password must be at least 8 characters long.'))

        return cleaned_data

    def save(self, commit=True):
        user = super(NutritionistForm, self).save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

#----------------------------------------------------------------------------------------------------------------------#

# Esta clase hereda de NutritionistForm y define un formulario que será utilizado para la creación y edición de instancias de usuarios con el rol de asistente en el sistema.
# El formulario incluye los mismos campos que NutritionistForm, pero el campo is_superuser es reemplazado por el campo is_staff.

class AssistantForm(NutritionistForm):
    class Meta(NutritionistForm.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'is_staff')


    def save(self, commit=True):
        user = super(AssistantForm, self).save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user

#----------------------------------------------------------------------------------------------------------------------#

# Esta clase define un formulario que será utilizado para la creación y edición de instancias de pacientes en el sistema.
# El formulario incluye campos para el nombre, apellidos, fecha de nacimiento, sexo, altura, peso e indicación de si realiza actividad aeróbica.

class PatientForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de nacimiento (formato yyyy-mm-dd)')


    class Meta:
        model = Patient
        fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 'sexo', 'altura', 'peso', 'actividad_aerobica', 'is_active')
        labels = {
            'nombre': _('Nombre'),
            'apellido_paterno': _('Apellido paterno'),
            'apellido_materno': _('Apellido materno'),
            'fecha_nacimiento': _('Fecha de Nacimiento'),
            'sexo': _('Sexo'),
            'altura': _('Altura (metros)'),
            'peso': _('Peso Inicial (kg)'),
            'actividad_aerobica': _('¿Realiza actividad aeróbica?'),
            'is_active': _('¿Está activo?'),
        }

#----------------------------------------------------------------------------------------------------------------------#

# Esta clase define un formulario que será utilizado para buscar un paciente en el sistema por su ID.

class SearchPatientForm(forms.Form):
    patient_id = forms.IntegerField(label='Ingrese su ID de paciente')
# ----------------------------------------------------------------------------------------------------------------------#

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['patient', 'peso', 'observaciones']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        consultation = super().save(commit=False)
        consultation.fecha_consulta = datetime.now()
        if commit:
            consultation.save()
        return consultation