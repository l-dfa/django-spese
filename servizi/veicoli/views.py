# veicoli/views.py
''' app veicoli views

    ldfa @ 2016.11.12 iniziale
'''
# python debugging
import pdb
import sys
import logging
log = logging.getLogger(__name__)       # log.debug, info, warning, error, critical("Hey there it works!!")
# django managing requests
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

# django forms
from django.forms import modelform_factory
from django.utils import timezone
# from django.core.exceptions import ValidationError
# from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

# django authorization
from django.contrib.auth.decorators import login_required

# django models
from django.db import transaction
from django.db.models import Max

# spese & taggit
from spese.models import Expense, Account
from spese.forms import ExpenseForm
from spese.utils import get_accounts
from taggit.models import Tag
from .models import VEvent, Vehicle, Event
from .forms import EventForm


@login_required(login_url="/login/")
def add(request):
    page_identification = 'Veicoli: new event'
    accounts = Account.objects.filter(users=request.user)
    vehicles = Vehicle.objects.filter(user=request.user)
    vevents = VEvent.objects.all()
    most_probable_vevent = VEvent.objects.all()[0]
    ### TRACE ### pdb.set_trace()
    km__max = Event.objects.all().aggregate(Max('km'))
    last_km = km__max['km__max'] if 'km__max' in km__max else 0
    account_selected = None
    tags_selected = []
    vehicle_selected = None
    vevent_selected = None
    if request.method == "POST":
        form1 = ExpenseForm(request.POST, prefix='form1')
        form2 = EventForm(request.POST, prefix='form2')
        account_selected = int(request.POST['account'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        vehicle_selected = int(request.POST['vehicle'])
        vevent_selected = int(request.POST['vevent'])
        if form1.is_valid() and form2.is_valid():
            try:
                with transaction.atomic():
                    expense = form1.save(commit=False)
                    expense.user = request.user
                    expense.account = Account.objects.get(id=account_selected)
                    expense.save()
                    tags = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
                    expense.tags.set(*tags, clear=True)
                    expense.save()
                    
                    event = form2.save(commit=False)
                    event.expense = expense
                    event.vehicle = Vehicle.objects.get(id=vehicle_selected)
                    event.vevent = VEvent.objects.get(id=vevent_selected)
                    event.save()
                    
                    ### TRACE ### pdb.set_trace()
                    msg =  'success creating expense {}, event {} for user {}, vehicle {} '.format(expense.id, event.id, expense.user.username, event.vehicle.name)
                    log.info(msg)
                    messages.success(request, msg)
            except:
                # error: Redisplay the expense change form
                msg = 'Error <{}> while trying to create expense'.format(sys.exc_info()[0])
                log.error(msg)
                messages.error(request, msg)
            else:
                ### TRACE ###                pdb.set_trace()
                if 'save' in request.POST.keys():
                    return HttpResponseRedirect(reverse('veicoli:detail', args=(expense.id,)))
    else:
        form1 = ExpenseForm(initial={
                              'description': most_probable_vevent.description,
                              'date': timezone.now(),
                              }, prefix='form1')
        form2 = EventForm(initial={
                             'km': last_km,
                             'unit_cost': 1,
                             }, prefix='form2')
    alltags = Tag.objects.all()
    return render(request, 'veicoli/add.html', { 'page_identification': page_identification,
                               'operation': 'new',
                               'form1': form1,
                               'form2': form2,
                               'accounts': accounts,
                               'account_selected': account_selected,
                               'alltags':  alltags,
                               'tags_selected': tags_selected,
                               'vehicles': vehicles,
                               'vehicle_selected': vehicle_selected,
                               'vevents': vevents,
                               'vevent_selected':  vevent_selected, 
                               })

@login_required(login_url='/login/')
def index(request):
    page_identification = 'Veicoli'
    event_expense_list = [event.expense.pk for event in Event.objects.all()]
    event_list = Event.objects.filter(expense__user=request.user).order_by('vehicle', '-expense__date')      #######   SVILUPPO
    ### TRACE ###    pdb.set_trace()
    return render(request, 'veicoli/index.html', {'page_identification': page_identification,
                                                  'event_list': event_list,
                                                }
                 )

@login_required(login_url="login/")
def detail(request, expense_id):
    #pdb.set_trace()
    expense = get_object_or_404(Expense, pk=expense_id)
    event = get_object_or_404(Event, expense=expense_id)
    page_identification = 'Veicoli: show event detail'
    if not expense.user == request.user:
        msg = "expense id {}: wrong user (it's {})".format(expense.id, expense.user.username)
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('veicoli:index'))
    return render(request, 'veicoli/detail.html', {'page_identification': page_identification,
                                                   'operation': 'show',
                                                   'expense': expense,
                                                   'event': event,
                                                }
                 )

