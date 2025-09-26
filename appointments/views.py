from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import calendar
import json
from .models import Appointment
from .forms import AppointmentForm


@login_required
def appointment_list(request):
    """Exibe uma lista paginada de compromissos do usuário com opções de filtragem."""
    appointments = Appointment.objects.filter(user=request.user).select_related('user')

    # Filtros
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    date_filter = request.GET.get('date')
    search_query = request.GET.get('search')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if type_filter:
        appointments = appointments.filter(type=type_filter)

    if date_filter:
        try:
            appointments = appointments.filter(date=date_filter)
        except (ValueError, TypeError):
            pass

    if search_query:
        appointments = appointments.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Paginação
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': Appointment.STATUS_CHOICES,
        'type_choices': Appointment.TYPE_CHOICES,
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_detail(request, pk):
    """Exibe os detalhes de um compromisso específico do usuário."""
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def appointment_create(request):
    """Cria um novo compromisso para o usuário logado."""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Compromisso criado com sucesso!')
            return redirect('main_dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AppointmentForm()
        form.fields['date'].initial = date.today()

    context = {
        'form': form,
        'title': 'Criar Compromisso'
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_update(request, pk):
    """Atualiza os detalhes de um compromisso existente do usuário."""
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compromisso atualizado com sucesso!')
            return redirect('main_dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AppointmentForm(instance=appointment)

    context = {
        'form': form,
        'appointment': appointment,
        'title': 'Editar Compromisso'
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_delete(request, pk):
    """Exclui um compromisso existente do usuário."""
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Compromisso excluído com sucesso!')
        return redirect('main_dashboard')

    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_confirm_delete.html', context)


@login_required
def appointments_dashboard(request):
    """View para o dashboard de appointments - compatível com AJAX"""
    try:
        today = timezone.now().date()
        
        # Appointments de hoje
        appointments_today = Appointment.objects.filter(
            user=request.user,
            date=today
        ).order_by('start_time')
        
        # Próximos appointments (próximos 7 dias)
        next_week = today + timedelta(days=7)
        appointments_upcoming = Appointment.objects.filter(
            user=request.user,
            date__range=[today + timedelta(days=1), next_week]
        ).order_by('date', 'start_time')
        
        # Appointments passados (últimos 30 dias)
        last_month = today - timedelta(days=30)
        appointments_past = Appointment.objects.filter(
            user=request.user,
            date__range=[last_month, today - timedelta(days=1)]
        ).order_by('-date', '-start_time')[:10]
        
        context = {
            'appointments_today': appointments_today,
            'appointments_upcoming': appointments_upcoming,
            'appointments_past': appointments_past,
            'today': today,
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'appointments/partials/dashboard_content.html', context)
        
        return render(request, 'appointments/dashboard.html', context)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro na view appointments_dashboard: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        else:
            context = {'error': 'Erro ao carregar appointments'}
            return render(request, 'appointments/dashboard.html', context, status=500)


@login_required
def appointment_calendar(request):
    """Exibe um calendário com os compromissos do usuário para um mês específico."""
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        if month < 1 or month > 12:
            month = timezone.now().month
        if year < 1900 or year > 2100:
            year = timezone.now().year
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])

    appointments = Appointment.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date', 'start_time')

    appointments_by_date = {}
    for appointment in appointments:
        date_key = appointment.date.strftime('%Y-%m-%d')
        if date_key not in appointments_by_date:
            appointments_by_date[date_key] = []
        appointments_by_date[date_key].append(appointment)

    cal = calendar.monthcalendar(year, month)

    context = {
        'calendar': cal,
        'appointments_by_date': appointments_by_date,
        'current_month': month,
        'current_year': year,
        'month_name': calendar.month_name[month],
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'now': timezone.now().date(),
    }
    return render(request, 'appointments/appointment_calendar.html', context)

@login_required
def update_appointment_status(request, pk):
    """Atualiza o status de um compromisso via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES).keys():
            appointment.status = new_status
            appointment.save()
            return JsonResponse({
                'success': True,
                'new_status_label': appointment.get_status_display(),
                'new_status_class': f'status-{appointment.status}'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Status inválido'})
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=400)
