# spese/forms.py
# python debugging
import pdb

# django and app
from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ( 'work_cost_type', 'date', 'description', 'amount', )
        # widgets = {
        #     'tags': forms.HiddenInput(),
        # }

class TransferFundsForm(ExpenseForm):
    CHOICES = (
         ('EXMPL', 'Example'),
    )
    tf_source = forms.ChoiceField(label='transfer account: source', required=True, choices=CHOICES)
    tf_destination = forms.ChoiceField(label='transfer account: destination', required=True, choices=CHOICES)
    
    def __init__(self, *args, **kwargs):
        '''
        thanks to 
        - lastmikoi@http://stackoverflow.com/questions/17392459/django-form-setting-choicefield-options-as-form-is-called
        - Daniel Roseman@http://stackoverflow.com/questions/14322185/init-got-multiple-values-for-keyword-argument
        '''
        custom_choices = kwargs.pop('custom_choices', None)        # from daniel roseman
        super(TransferFundsForm, self).__init__(*args, **kwargs)
        if custom_choices:
            self.fields['tf_source'].choices = custom_choices      # from lastmikoi
            self.fields['tf_destination'].choices = custom_choices
