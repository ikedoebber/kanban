from django import forms
from .models import Appointment
from datetime import datetime


def get_time_choices(step_minutes=15):
    choices = []
    for hour in range(24):
        for minute in range(0, 60, step_minutes):
            time_str = f"{hour:02d}:{minute:02d}"
            choices.append((time_str, time_str))
    return choices


class AppointmentForm(forms.ModelForm):
    start_time = forms.ChoiceField(
        choices=get_time_choices(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    end_time = forms.ChoiceField(
        choices=get_time_choices(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = [
            'title', 'description', 'appointment_type', 'priority', 
            'status', 'date', 'start_time', 'end_time', 'location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do compromisso'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Digite a descrição do compromisso'
            }),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o local do compromisso'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time_str = cleaned_data.get('start_time')
        end_time_str = cleaned_data.get('end_time')

        if start_time_str and end_time_str:
            try:
                # Converte strings 'HH:MM' para objetos de tempo comparáveis
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except ValueError:
                raise forms.ValidationError('Formato de horário inválido.')

            # Verifica se o horário de término é anterior ou igual ao de início
            if end_time <= start_time:
                raise forms.ValidationError(
                    'O horário de término deve ser **posterior** ao horário de início.'
                )

        return cleaned_data
