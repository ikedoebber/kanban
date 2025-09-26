from django.urls import path
from . import views


app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('dashboard/', views.task_dashboard, name='task_dashboard'),
    path('board/', views.tasks_board, name='tasks_board'),
    path('create/', views.task_create, name='task_create'),
    path('update-status/', views.update_task_status, name='update_status'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/edit/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
]
