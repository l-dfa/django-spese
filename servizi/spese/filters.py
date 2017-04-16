# spese/filters.py

#import pdb
import django_filters
from .models import Expense, Account, WCType

def accounts(request):
    return Account.objects.filter(users__in=[request.user,])
    
class ExpenseFilter(django_filters.FilterSet):
    account = django_filters.ModelChoiceFilter(queryset=accounts)
    not_for_work = django_filters.BooleanFilter(name='work_cost_type', lookup_expr='isnull', label='Unrelated to work')
    date = django_filters.DateFromToRangeFilter()
    description = django_filters.CharFilter(name='description', lookup_expr='icontains')
    class Meta:
        model = Expense
        fields = [ ]
