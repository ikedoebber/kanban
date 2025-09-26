from django.urls import path
from . import views


app_name = 'goals'

urlpatterns = [
    path('', views.goal_list, name='goal_list'),
    path('dashboard/', views.goal_dashboard, name='goal_dashboard'),
    path('board/', views.goals_board, name='goals_board'),
    path('create/', views.goal_create, name='goal_create'),
    path('update-period/', views.update_goal_period, name='update_period'),
    path('<int:pk>/', views.goal_detail, name='goal_detail'),
    path('<int:pk>/edit/', views.goal_update, name='goal_update'),
    path('<int:pk>/delete/', views.goal_delete, name='goal_delete'),
]
