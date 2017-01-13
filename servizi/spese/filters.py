# spese/filters.py
#import pdb
import django_filters
from .models import Expense, Account

def accounts(request):
    return Account.objects.filter(users__in=[request.user,])
    
class ExpenseFilter(django_filters.FilterSet):
    account = django_filters.ModelChoiceFilter(queryset=accounts)
    date = django_filters.DateFromToRangeFilter()
    class Meta:
        model = Expense
        fields = [ ]
