# veicoli/forms.py
# python debugging
import pdb

# django and app
from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ( 'km', 'unit_cost', )
