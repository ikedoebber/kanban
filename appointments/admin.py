from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'appointment_type', 'priority', 'status', 'user', 'date', 'start_time', 'is_today', 'is_upcoming']
    list_filter = ['appointment_type', 'priority', 'status', 'user', 'date']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    
    def is_today(self, obj):
        return obj.is_today
    is_today.boolean = True
    is_today.short_description = 'Hoje'
    
    def is_upcoming(self, obj):
        return obj.is_upcoming
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Futuro'
