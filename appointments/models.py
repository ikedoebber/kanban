from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Appointment(models.Model):
    PRIORITY_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
    ]
    
    TYPE_CHOICES = [
        ('reuniao', 'Reunião'),
        ('ligacao', 'Ligação'),
        ('evento', 'Evento'),
        ('consulta', 'Consulta'),
        ('outro', 'Outro'),
    ]
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    appointment_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='reuniao', 
        verbose_name='Tipo'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='media', 
        verbose_name='Prioridade'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='agendado', 
        verbose_name='Status'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Usuário'
    )
    date = models.DateField(verbose_name='Data')
    start_time = models.TimeField(verbose_name='Horário de início')
    end_time = models.TimeField(verbose_name='Horário de término')
    location = models.CharField(max_length=300, blank=True, verbose_name='Local')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Compromisso'
        verbose_name_plural = 'Compromissos'
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.start_time}"
    
    def get_absolute_url(self):
        return reverse('appointment_detail', kwargs={'pk': self.pk})
    
    @property
    def is_today(self):
        return self.date == timezone.now().date()
    
    @property
    def is_upcoming(self):
        return self.date > timezone.now().date()
    
    @property
    def duration(self):
        """Retorna a duração do compromisso em minutos"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return int(duration.total_seconds() / 60)
