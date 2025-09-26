from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from datetime import timedelta

# Importe modelos no topo
from tasks.models import Task
from goals.models import Goal
from appointments.models import Appointment

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Login realizado com sucesso! Bem-vindo(a), {user.get_full_name() or user.username}.')
                
                next_page = request.GET.get('next')
                if next_page and url_has_allowed_host_and_scheme(next_page, allowed_hosts={request.get_host()}):
                    return redirect(next_page)
                return redirect('main_dashboard')
            else:
                messages.error(request, 'Credenciais inválidas. Verifique seu usuário e senha.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('login')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from itertools import chain

from tasks.models import Task
from goals.models import Goal
from appointments.models import Appointment


@login_required
def main_dashboard(request):
    user = request.user
    
    # --- Tarefas ---
    base_tasks = Task.objects.filter(assigned_to=user).select_related('assigned_to')
    
    todo_tasks = base_tasks.filter(status='todo').order_by('-priority', '-created_at')[:10]
    in_progress_tasks = base_tasks.filter(status='in_progress').order_by('-priority', '-created_at')[:10]
    done_tasks = base_tasks.filter(status='done').order_by('-updated_at')[:10]
    
    task_stats = {
        'total_tasks': base_tasks.count(),
        'pending_tasks': base_tasks.filter(status='todo').count(),
        'in_progress_tasks': base_tasks.filter(status='in_progress').count(),
        'completed_tasks': base_tasks.filter(status='done').count(),
        'overdue_tasks': base_tasks.filter(
            due_date__lt=timezone.now(), 
            status__in=['todo', 'in_progress']
        ).count(),
    }
    
    # --- Metas ---
    base_goals = Goal.objects.filter(created_by=user).select_related('created_by')
    
    goals_weekly = base_goals.filter(period='weekly')
    goals_monthly = base_goals.filter(period='monthly')
    goals_quarterly = base_goals.filter(period='quarterly')
    goals_biannual = base_goals.filter(period='biannual')  # ✅ Correto
    goals_annual = base_goals.filter(period='annual')

    recent_goals = base_goals.order_by('-created_at')[:5]
    
    goal_stats = {
        'total_goals': base_goals.count(),
        'pending_goals': base_goals.filter(status='not_started').count(),
        'in_progress_goals': base_goals.filter(status='in_progress').count(),
        'completed_goals': base_goals.filter(status='completed').count(),
        'overdue_goals': base_goals.filter(
            due_date__lt=timezone.now(), 
            status__in=['not_started', 'in_progress']
        ).count(),
    }
    
    # --- Compromissos ---
    today = timezone.localdate()
    base_appointments = Appointment.objects.filter(user=user).select_related('user')
    
    # Hoje
    today_appointments = base_appointments.filter(date=today).order_by('start_time')[:5]
    
    # Próximos 7 dias
    next_week = today + timedelta(days=7)
    upcoming_appointments = base_appointments.filter(
        date__gt=today,
        date__lte=next_week
    ).order_by('date', 'start_time')[:5]
    
    # Combinar hoje + futuros (máx 6)
    all_recent_appointments = list(chain(today_appointments, upcoming_appointments))
    all_recent_appointments = sorted(all_recent_appointments, key=lambda x: (x.date, x.start_time))[:6]
    
    appointment_stats = {
        'total_appointments': base_appointments.count(),
        'today_appointments': base_appointments.filter(date=today).count(),
        'upcoming_appointments': base_appointments.filter(date__gt=today).count(),
        'confirmed_appointments': base_appointments.filter(status='confirmado').count(),
        'urgent_appointments': base_appointments.filter(priority='urgente').count(),
    }
    
    context = {
        'page_title': 'Dashboard',
        'user': user,
        
        # Tarefas
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'task_stats': task_stats,
        
        # Metas
        'goals_weekly': goals_weekly,
        'goals_monthly': goals_monthly,
        'goals_quarterly': goals_quarterly,
        'goals_biannual': goals_biannual,  # ✅ Variável correta
        'goals_annual': goals_annual,
        'recent_goals': recent_goals,
        'goal_stats': goal_stats,
        
        # Compromissos
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'all_recent_appointments': all_recent_appointments,
        'appointment_stats': appointment_stats,
    }
    
    return render(request, 'main_dashboard.html', context)
