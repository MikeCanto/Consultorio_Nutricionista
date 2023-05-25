import time
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponseForbidden, HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import logout

from .forms import PatientForm, SearchPatientForm, AssistantForm, NutritionistForm, ConsultationForm
from .models import Patient, Consultation
import logging
logger = logging.getLogger(__name__)


@login_required
def home(request):
    return render(request, 'home.html', {'section': 'home'})


# @login_required
# def view_patients(request):
#     patients = Patient.objects.all()
#     return render(request, 'view_patients.html', {'patients': patients})

def logout_view(request):
    logout(request)
    return redirect('login')

def access_denied(request):
    return render(request, 'access_denied.html')

def view_patients(request, option=None):
    if option == 'pagination':
        if request.user.is_staff and not request.user.is_superuser:
            return redirect('access_denied')
        else:
            # Lógica para mostrar la lista de pacientes en paginación
            # Obtener la lista de pacientes activos
            patients = Patient.objects.filter(is_active=True).order_by('apellido_paterno')

            # Implementar la paginación
            paginator = Paginator(patients, 5)  # Mostrar 5 pacientes por página
            page = request.GET.get('page')
            patients_page = paginator.get_page(page)
            return render(request, 'view_patients_pagination.html', {'patients': patients_page})
    else:
        # Lógica para mostrar la lista de pacientes en orden ascendente por apellidos
        # Obtener la lista de pacientes activos ordenados por apellidos
        patients = Patient.objects.filter(is_active=True).order_by('apellido_paterno')

        return render(request, 'view_patients.html', {'patients': patients})


@login_required
def view_assistants(request):
    assistants = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    return render(request, 'view_assistants.html', {'assistants': assistants})

@login_required
def delete_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    patient.delete()
    return redirect('view_patients')

@login_required
def delete_assistant(request, assistant_id):
    assistant = get_object_or_404(User, id=assistant_id, is_staff=True, is_superuser=False)
    if request.method == 'POST':
        assistant.delete()
        messages.success(request, 'Assistant has been deleted.')
        return redirect('view_assistants')
    return render(request, 'delete_assistant.html', {'assistant': assistant})

@login_required
def edit_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('view_patients')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'edit_patient.html', {'form': form, 'patient': patient})

@login_required
def edit_assistant(request, assistant_id):
    assistant = User.objects.get(id=assistant_id)
    if not assistant.is_staff or assistant.is_superuser:
        # Si el usuario no es un assistant, redirigir a la vista de asistentes.
        return redirect('view_assistants')

    if request.method == 'POST':
        form = AssistantForm(request.POST, instance=assistant)
        if form.is_valid():
            form.save()
            return redirect('view_assistants')
    else:
        form = AssistantForm(instance=assistant)

    return render(request, 'edit_assistant.html', {'form': form, 'assistant': assistant})

def base_view(request):
    return render(request, 'base.html')


@login_required
def add_assistant(request):
    if request.method == 'POST':
        assistant_form = AssistantForm(request.POST)
        if assistant_form.is_valid():
            new_assistant = assistant_form.save(commit=False)
            new_assistant.set_password(assistant_form.cleaned_data['password'].encode())
            new_assistant.save()
            return render(request, 'assistant_added.html', {'new_assistant': new_assistant})
    else:
        assistant_form = AssistantForm()
        return render(request, 'add_assistant.html', {'assistant_form': assistant_form})


@login_required
def add_nutritionist(request):
    if request.method == 'POST':
        nutritionist_form = NutritionistForm(request.POST)
        if nutritionist_form.is_valid():
            new_nutritionist = nutritionist_form.save(commit=False)
            new_nutritionist.set_password(nutritionist_form.cleaned_data['password'].encode())
            new_nutritionist.save()
            return render(request, 'nutritionist_added.html', {'new_nutritionist': new_nutritionist})
    else:
        nutritionist_form = NutritionistForm()

    return render(request, 'add_nutritionist.html', {'nutritionist_form': nutritionist_form})


@login_required
def add_patient(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = PatientForm(request.POST)
            if form.is_valid():
                patient = form.save(commit=False)
                patient.user = request.user
                patient.save()
                messages.success(request, 'El paciente se ha agregado correctamente')
                return render(request, 'patient_added.html', {'patient': patient})
        else:
            form = PatientForm()
        return render(request, 'add_patient.html', {'form': form})
    else:
        return render(request, 'view_patients.html', {'section','home'}) #//


@login_required
def patient_progress(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, user=request.user)
    return render(request, 'patient_progress.html', {'patient': patient})

@login_required
def patient_list(request):
    patients = Patient.objects.filter(user=request.user)
    return render(request, 'patient_list.html', {'patients': patients})


@login_required
def patient_detail(request, patient_id):
    # Retrieve the patient object from the database
    patient = get_object_or_404(Patient, id=patient_id)

    # Check if the user is an administrator or an assistant
    is_admin = request.user.is_superuser
    is_assistant = request.user.is_staff and not request.user.is_superuser

    # If the user is an administrator or the patient's assigned nutritionist, allow full access
    if is_admin or is_assistant:
        return render(request, 'patient_detail.html', {'patient': patient})
    # Otherwise, deny access
    else:
        return render(request, 'access_denied.html')




def patient_public_detail(request, patient_id):
    try:
        # Buscar paciente por ID
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        # Manejar el caso de que no se encuentre el paciente
        return HttpResponse("No se encontró el paciente con ese ID")

    # Renderizar plantilla con información del paciente
    context = {'patient': patient}
    return render(request, 'patient_public_detail.html', context)


def search_patient(request):
    try:
        if request.method == 'POST':
            form = SearchPatientForm(request.POST)
            if form.is_valid():
                patient_id = form.cleaned_data['patient_id']
                patient = get_object_or_404(Patient, id=patient_id)
                print(f"Patient found: {patient}") #debug
                context = {'form': form, 'patient': patient}
                return render(request, 'patient_public_form.html', context)
            else:
                print(f"Form errors: {form.errors}")  # debug
                raise Exception("Invalid form data")
        else:
            form = SearchPatientForm()
            context = {'form': form}
            return render(request, 'patient_public_form.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")  # debug
        return redirect('patient_public_not_found')




@login_required
def initiate_consultation(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.fecha_consulta = datetime.now()
            consultation.save()

            # Obtener el paciente seleccionado en el formulario
            patient = form.cleaned_data['patient']

            # Actualizar el peso del paciente
            patient.peso = consultation.peso
            patient.save()

            # Redireccionar a la página de detalle de consulta
            return redirect('consultation_detail', consultation.id)
    else:
        form = ConsultationForm()

    patients = Patient.objects.filter(is_active=True)  # Filtrar pacientes activos
    return render(request, 'initiate_consultation.html', {'form': form, 'patients': patients})


def consultation_detail(request, consultation_id):
    # Obtener la consulta por su ID
    try:
        consultation = Consultation.objects.get(id=consultation_id)
    except Consultation.DoesNotExist:
        return HttpResponse('La consulta no existe')

    # Renderizar el template de detalle de consulta
    return render(request, 'consultation_detail.html', {'consultation': consultation})

def patient_public_not_found(request):
    try:
        return render(request, 'patient_public_not_found.html')
    except Exception as e:
        print(f"Error: {str(e)}")  # debug
        return HttpResponseServerError()
