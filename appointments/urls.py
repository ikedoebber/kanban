from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('dashboard/', views.appointments_dashboard, name='appointments_dashboard'),
    path('calendar/', views.appointment_calendar, name='appointment_calendar'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('<int:pk>/update-status/', views.update_appointment_status, name='update_appointment_status'),
]
