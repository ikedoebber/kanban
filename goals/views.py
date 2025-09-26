from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import json
from .models import Goal
from .forms import GoalForm
import logging

@login_required
def goal_list(request):
    """Exibe uma lista paginada de metas com opções de filtragem."""
    goals = Goal.objects.filter(created_by=request.user)

    # Filtros
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    period_filter = request.GET.get('period')
    search_query = request.GET.get('search')

    if status_filter:
        goals = goals.filter(status=status_filter)

    if priority_filter:
        goals = goals.filter(priority=priority_filter)

    if period_filter:
        goals = goals.filter(period=period_filter)

    if search_query:
        goals = goals.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Paginação
    paginator = Paginator(goals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': Goal.STATUS_CHOICES,
        'priority_choices': Goal.PRIORITY_CHOICES,
        'period_choices': Goal.PERIOD_CHOICES,
    }
    return render(request, 'goals/goal_list.html', context)


@login_required
def goal_detail(request, pk):
    """Exibe os detalhes de uma meta específica."""
    goal = get_object_or_404(Goal, pk=pk, created_by=request.user)
    context = {'goal': goal}
    return render(request, 'goals/goal_detail.html', context)


@login_required
def goal_create(request):
    """Cria uma nova meta."""
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()
            messages.success(request, 'Meta criada com sucesso!')
            return redirect('main_dashboard')
    else:
        form = GoalForm()

    context = {
        'form': form,
        'title': 'Criar Meta'
    }
    return render(request, 'goals/goal_form.html', context)


@login_required
def goal_update(request, pk):
    """Atualiza os detalhes de uma meta existente."""
    goal = get_object_or_404(Goal, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta atualizada com sucesso!')
            return redirect('main_dashboard')
    else:
        form = GoalForm(instance=goal)

    context = {
        'form': form,
        'goal': goal,
        'title': 'Editar Meta'
    }
    return render(request, 'goals/goal_form.html', context)


@login_required
def goal_delete(request, pk):
    """Exclui uma meta existente."""
    goal = get_object_or_404(Goal, pk=pk, created_by=request.user)

    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Meta excluída com sucesso!')
        return redirect('main_dashboard')

    context = {'goal': goal}
    return render(request, 'goals/goal_confirm_delete.html', context)


@login_required
def goal_dashboard(request):
    """Dashboard com estatísticas das metas do usuário."""
    user_goals = Goal.objects.filter(created_by=request.user)

    context = {
        'total_goals': user_goals.count(),
        'pending_goals': user_goals.filter(status='active').count(),
        'completed_goals': user_goals.filter(status='completed').count(),
        'paused_goals': user_goals.filter(status='paused').count(),
        'recent_goals': user_goals.order_by('-created_at')[:5],
    }
    return render(request, 'goals/dashboard.html', context)


@login_required
def goals_board(request):
    """view para o board de goals - compatível com ajax"""
    try:
        print(f"usuário logado: {request.user.username} (id: {request.user.id})")

        goals_weekly = Goal.objects.filter(created_by=request.user, period='weekly').order_by('-created_at')
        goals_monthly = Goal.objects.filter(created_by=request.user, period='monthly').order_by('-created_at')
        goals_quarterly = Goal.objects.filter(created_by=request.user, period='quarterly').order_by('-created_at')
        goals_biannual = Goal.objects.filter(created_by=request.user, period='biannual').order_by('-created_at')
        goals_annual = Goal.objects.filter(created_by=request.user, period='annual').order_by('-created_at')

        print(f"metas do usuário (weekly): {goals_weekly.count()}")
        print(f"metas do usuário (monthly): {goals_monthly.count()}")
        print(f"metas do usuário (quarterly): {goals_quarterly.count()}")
        print(f"metas do usuário (biannual): {goals_biannual.count()}")
        print(f"metas do usuário (annual): {goals_annual.count()}")

        context = {
            'goals_weekly': goals_weekly,
            'goals_monthly': goals_monthly,
            'goals_quarterly': goals_quarterly,
            'goals_biannual': goals_biannual,
            'goals_annual': goals_annual,
        }

        if request.headers.get('x-requested-with') == 'xmlhttprequest':
            return render(request, 'goals/partials/board_content.html', context)

        return render(request, 'goals/board.html', context)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"erro na view goals_board: {str(e)}")

        if request.headers.get('x-requested-with') == 'xmlhttprequest':
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=500)
        else:
            context = {'error': 'erro ao carregar goals'}
            return render(request, 'goals/board.html', context, status=500)



logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
def update_goal_period(request):
    """Atualiza o período de uma meta via AJAX"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        goal_id = data.get('id')
        new_period = data.get('period')

        if not goal_id or not new_period:
            return JsonResponse({'error': 'ID e período são obrigatórios.'}, status=400)

        # Verifica se o período é válido
        period_choices = [choice[0] for choice in Goal.PERIOD_CHOICES]
        if new_period not in period_choices:
            return JsonResponse({'error': 'Período inválido.'}, status=400)

        # Busca a meta e atualiza
        goal = get_object_or_404(Goal, id=goal_id, created_by=request.user)
        goal.period = new_period
        goal.save(update_fields=['period'])

        return JsonResponse({
            'success': True,
            'message': 'Período atualizado com sucesso.',
            'goal_id': goal_id,
            'new_period': new_period
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        logger.exception(f"Erro ao atualizar período da meta {goal_id if 'goal_id' in locals() else 'desconhecida'}")
        return JsonResponse({'error': 'Erro interno ao atualizar a meta.'}, status=500)
