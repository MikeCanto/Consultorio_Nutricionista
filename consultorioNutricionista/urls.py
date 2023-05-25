"""
URL configuration for consultorioNutricionista project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'consultorioNutricionista'


urlpatterns = [
    # Basic urls
    path('admin/', admin.site.urls),
    path('', views.base_view, name='base'),
    path('home/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('login_fail/', auth_views.login_required(), name='login_fail'),
    path('logout/', views.logout_view, name='logout'),
    path('access-denied/', views.access_denied, name='access_denied'),


    # 'View' urls
    path('patients/', views.view_patients, name='view_patients'),
    path('view-patients/pagination/', views.view_patients, {'option': 'pagination'}, name='view_patients_pagination'),
    path('patients/list/', views.view_patients, {'option': 'list'}, name='view_list_patients'),
    path('assistants/', views.view_assistants, name='view_assistants'),
    path('patient_list/', views.patient_list, name='patient_list'),
    path('patient_progress/<int:patient_id>/', views.patient_progress, name='patient_progress'),
    path('patient_detail/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    # Ruta para iniciar la consulta
    path('patient/initiate-consultation/', views.initiate_consultation, name='initiate_consultation'),
    path('patient/consultation-detail/<int:consultation_id>/', views.consultation_detail, name='consultation_detail'),

    # 'Add' urls
    path('patients/add/', views.add_patient, name='add_patient'),
    path('nutritionist/add/', views.add_nutritionist, name='add_nutritionist'),
    path('assistants/add/', views.add_assistant, name='add_assistant'),

    # 'Edit' urls
    path('patients/edit/<int:pk>/', views.edit_patient, name='edit_patient'),
    path('assistants/edit/<int:pk>/', views.edit_assistant, name='edit_assistant'),

    # 'Delete' urls
    path('patients/delete/<int:pk>/', views.delete_patient, name='delete_patient'),
    path('assistants/delete/<int:pk>/', views.delete_assistant, name='delete_assistant'),

    # Public urls
    path('patient_public_detail/<int:patient_id>/', views.patient_public_detail, name='patient_public_detail'),
    path('patient_public_not_found/', views.patient_public_not_found, name='patient_public_not_found'),
    path('patient_public_form/', views.search_patient, name='search_patient'),
    path('patient_public_form/', views.search_patient, name='patient_public_form'),
]

