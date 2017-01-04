# spese/filters.py
# import pdb
import django_filters
from .models import Expense, Account

class ExpenseFilter(django_filters.FilterSet):
    # user = django_filters.ModelChoiceFilter(name='user')
    account = django_filters.ModelChoiceFilter(queryset=Account.objects.all())
    date = django_filters.DateFromToRangeFilter()
    class Meta:
        model = Expense
        fields = [ ]