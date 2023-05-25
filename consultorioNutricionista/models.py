from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# La clase Patient es un modelo que representa la información de un paciente en el sistema

class Patient(models.Model):
    nombre = models.CharField(max_length=50, blank=False, null=False)
    apellido_paterno = models.CharField(max_length=50, blank=False, null=False)
    apellido_materno = models.CharField(max_length=50, blank=False, null=False)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')], blank=False, null=False)
    altura = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    actividad_aerobica = models.BooleanField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return ' Paciente: ' + self.nombre + ' Apellido paterno: ' + self.apellido_paterno + ' Apellido materno: ' + self.apellido_materno + ' Fecha nacimiento: ' + str(self.fecha_nacimiento) + ' Sexo: ' + self.sexo + ' Altura: ' + str(self.altura) + ' Peso: ' + str(self.peso) + ' Actividad aeróbica: ' + str(self.actividad_aerobica)

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    observaciones = models.TextField()
    imc = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    class Meta:
        get_latest_by = 'fecha_consulta'

    def __str__(self):
        return f"Consulta del paciente: {self.patient}, Fecha: {self.fecha_consulta}"

def latest_imc(self):
    latest_consultation = Consultation.objects.filter(patient=self.patient).order_by('-fecha_consulta').first()
    if latest_consultation and latest_consultation.imc:
        return latest_consultation.imc
    return None

def previous_imc(self):
    latest_consultation = Consultation.objects.filter(patient=self.patient).order_by('-fecha_consulta').first()
    previous_consultation = Consultation.objects.filter(patient=self.patient, fecha_consulta__lt=latest_consultation.fecha_consulta).order_by('-fecha_consulta').first()
    if previous_consultation and previous_consultation.imc:
        return previous_consultation.imc
    return None

#----------------------------------------------------------------------------------------------------------------------#
@receiver(post_save, sender=Consultation)
def calculate_imc(sender, instance, created, **kwargs):
    if created:
        height = instance.patient.altura
        if height:
            imc = instance.peso / (height * height)
            instance.imc = round(imc, 2)
            instance.save()
