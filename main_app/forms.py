from django import forms 
from .models import Fare
from django.contrib.auth import get_user_model

class FareForm(forms.ModelForm):
    class Meta:
        model = Fare
        fields = ['name', 'amount', 'date', 'category', 'paid_by', 'split_between']
        widgets = {
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'placeholder': 'Select a date',
                    'type': 'date'
                }
            ),
        }