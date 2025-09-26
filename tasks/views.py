from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import json
from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):
    """Exibe uma lista paginada de tarefas com opções de filtragem."""
    tasks = Task.objects.filter(created_by=request.user)
    
    # Filtros
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, pk):
    """Exibe os detalhes de uma tarefa específica."""
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    context = {'task': task}
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create(request):
    """Cria uma nova tarefa."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Tarefa criada com sucesso!')
            return redirect('main_dashboard')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'Criar Tarefa'
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_update(request, pk):
    """Atualiza os detalhes de uma tarefa existente."""
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa atualizada com sucesso!')
            return redirect('main_dashboard')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': 'Editar Tarefa'
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, pk):
    """Exclui uma tarefa existente."""
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarefa excluída com sucesso!')
        return redirect('main_dashboard')
    
    context = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)


@login_required
def task_dashboard(request):
    """Dashboard com estatísticas das tarefas do usuário."""
    user_tasks = Task.objects.filter(created_by=request.user)
    
    context = {
        'total_tasks': user_tasks.count(),
        'pending_tasks': user_tasks.filter(status='todo').count(),
        'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
        'completed_tasks': user_tasks.filter(status='done').count(),
        'overdue_tasks': user_tasks.filter(
            due_date__lt=timezone.now(), 
            status__in=['todo', 'in_progress']
        ).count(),
        'recent_tasks': user_tasks.order_by('-created_at')[:5],
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def tasks_board(request):
    """View para o board de tasks - compatível com AJAX"""
    try:
        tasks_todo = Task.objects.filter(created_by=request.user, status='todo').order_by('-created_at')
        tasks_in_progress = Task.objects.filter(created_by=request.user, status='in_progress').order_by('-created_at')
        tasks_done = Task.objects.filter(created_by=request.user, status='done').order_by('-created_at')
        
        context = {
            'tasks_todo': tasks_todo,
            'tasks_in_progress': tasks_in_progress,
            'tasks_done': tasks_done,
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'tasks/partials/board_content.html', context)
        
        return render(request, 'tasks/board.html', context)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro na view tasks_board: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        else:
            context = {'error': 'Erro ao carregar tasks'}
            return render(request, 'tasks/board.html', context, status=500)


@login_required
@require_http_methods(["POST"])
def update_task_status(request):
    """Atualiza o status de uma tarefa via AJAX"""
    try:
        data = json.loads(request.body)
        task_id = data.get('id')
        new_status = data.get('status')

        if not task_id or not new_status:
            return JsonResponse({'error': 'ID e status são obrigatórios'}, status=400)

        if new_status not in dict(Task.STATUS_CHOICES):
            return JsonResponse({'error': 'Status inválido'}, status=400)

        task = get_object_or_404(Task, id=task_id, created_by=request.user)
        task.status = new_status
        task.save()

        return JsonResponse({
            'success': True,
            'message': 'Status atualizado com sucesso',
            'task_id': task_id,
            'new_status': new_status
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao atualizar status da task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
