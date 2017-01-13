# spese/filters.py
import pdb
import django_filters
from .models import Event, Vehicle

def vehicles(request):
    # pdb.set_trace()
    return Vehicle.objects.filter(user__in=[request.user,])
    
class EventFilter(django_filters.FilterSet):
    vehicle = django_filters.ModelChoiceFilter(queryset=vehicles)
    # date = django_filters.DateFromToRangeFilter()
    class Meta:
        model = Event
        fields = [ ]
