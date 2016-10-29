# spese/views.py
''' app spese views

    ldfa@2016.10.29 adding log facility in primary program points
        bug 0001: got a pdb error in transfer funds from production site.
                  after introducing the log facility it doesn't appair again.
                  it seems as I forgot a pdb.set_trace on. but it isn't in repository,
    ldfa@2016.09.11 added a project css:
           - servizi/static/css/servizi.css:  project specific css attributes
        reduced h1 height in servizi.css 
        added a page_identification block in base.html feeded from apps
    ldfa@2016.09.07-11  fighting to deploy the project to my production server
        releasing python+virtualenv+django in a centos 6+apache framework
        via mod_wsgi was harder than I aspected. However finally it worked!
    ldfa@...-2016.08.14 moving some css from project to app:
           - spese/static/spese/spese.css;   spese specific css attributes 
           - /servizi/template/base.html:    added {% block stylesheet %} 
           - spese/template/spese/*.html:    added {% load staticfiles %} and stylesheet block
        right justified the amount column in spese/template/spese/index.html
        adopted the css skeleton boilerplate (http://getskeleton.com/)
           modified spese/template/spese/*.html and /servizi/template/css/*.hmtl
        visual adjustments of User Interface
    ldfa@2016.08.08 moving login from app to project:
            - /servizi/templates/login.html; login template
            - /servizi/servizi/forms.py;     contains class LoginForm 
            - login_url="/login/";           project url (...="login/" would kept hostname/spes/login)
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
from django.db.models import Sum

# spese & taggit
from .models import Expense, Source
from .forms import ExpenseForm, TransferFundsForm
from .utils import get_sources
from taggit.models import Tag


@login_required(login_url="/login/")
def toggle(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    try:
        expense.amount = -expense.amount
        expense.save()
        msg = "success toggling expense id {} for user {}".format(expense.id, expense.user.username)
        log.info(msg)
        messages.success(request, msg)
    except:
        msg = 'Error <{}> while toggling expense {}'.format(sys.exc_info()[0], expense_id)
        log.error(msg)
        messages.error(request, msg)

    return HttpResponseRedirect(reverse('spese:detail', args=(expense.id,)))
                             

@login_required(login_url="/login/")
def add(request):
    page_identification = 'Spese: new expense'
    sources = Source.objects.filter(users=request.user)
    source_selected = None
    tags_selected = []
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        source_selected = int(request.POST['source'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.source = Source.objects.get(id=source_selected)
                expense.save()
                tags = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
                expense.tags.set(*tags, clear=True)
                expense.save()
                msg =  'success creating expense id {} for user {}'.format(expense.id, expense.user.username)
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
                    return HttpResponseRedirect(reverse('spese:detail', args=(expense.id,)))
    else:
        form = ExpenseForm(initial={
                              'description': 'expense description',
                              'date': timezone.now(),
                              })
    alltags = Tag.objects.all()
    return render(request, 'spese/add.html', { 'page_identification': page_identification,
                               'operation': 'new',
                               'form': form,
                               'sources': sources,
                               'source_selected': source_selected,
                               'alltags': alltags,
                               'tags_selected': tags_selected,
                               })

@login_required(login_url="/login/")
def transfer_funds(request):
    '''
    add transfer funds 
    '''
    page_identification = 'Spese: new transfer funds'
    source_choices = get_sources(request.user)
    if not source_choices or len(source_choices) < 2:
        msg = 'User {} has too little sources to do a transfer funds'.format(request.user.username)
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    source_selected = None
    if request.method == "POST":
        form = TransferFundsForm(request.POST, custom_choices=source_choices)
        if form.is_valid():
            try:
                ### TRACE ###                   pdb.set_trace()
                tf_source_id = int(form['tf_source'].value())
                tf_destination_id = int(form['tf_destination'].value())
                expense = form.save(commit=False)
                expense.user = request.user
                expense.source = Source.objects.get(id=tf_source_id)
                expense.save()                                           # setting source record id
                tags = ['transfer_funds']
                expense.tags.set(*tags, clear=True)                      # (this needs record id)
                expense.save()                                           # this is the complete source record, with tag
                expense.source = Source.objects.get(id=tf_destination_id)
                expense.amount = -expense.amount
                expense.pk = None                                        # https://docs.djangoproject.com/en/1.8/topics/db/queries/#copying-model-instances
                expense.save()                                           # setting destination id
                expense.tags.set(*tags, clear=True)
                expense.save()                                           # and this is the destination record
                msg =  'success transferring {} funds for user {}'.format(expense.amount, expense.user.username)
                log.info(msg)
                messages.success(request, msg)
                pass
            except:
                # error: Redisplay the expense change form
                msg = 'Error <{}> while trying to transfer funds'.format(sys.exc_info()[0])
                log.error(msg)
                messages.error(request, msg)
            else:
                return HttpResponseRedirect(reverse('spese:index'))
    else:
        form = TransferFundsForm(custom_choices=source_choices,
                                 initial={
                                     'description': 'transferring funds',
                                     'date': timezone.now(),
                                 })
    return render(request, 'spese/transfer_funds.html', {'page_identification': page_identification,
                                                         'operation': 'add',
                                                         'form': form,
                                                        }
                 )

                              
@login_required(login_url='/login/')
def index(request):
    page_identification = 'Spese'
    expenses_list = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'spese/index.html', {'page_identification': page_identification,
                                                'expenses_list': expenses_list,
                                                }
                 )
    
    
@login_required(login_url='/login/')
def balance(request):
    page_identification = 'Spese: Accounts balance'
    accounts_list = Source.objects.all()
    ###  TRACE  ###    pdb.set_trace()
    for account in accounts_list:
        sum = Expense.objects.filter(user=request.user, source=account, amount__gt=0).aggregate(Sum("amount"))
        account.positive = sum["amount__sum"] if sum else 0
        sum = Expense.objects.filter(user=request.user, source=account, amount__lt=0).aggregate(Sum('amount'))
        account.negative = sum["amount__sum"] if sum else 0
        account.balance    = account.positive + account.negative
    return render(request, 'spese/balance.html', {'page_identification': page_identification,
                                                'accounts_list': accounts_list,
                                                }
                 )

                 
@login_required(login_url="login/")
def detail(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    page_identification = 'Spese: show expense detail'
    if not expense.user == request.user:
        msg = "expense id {}: wrong user (it's {})".format(expense.id, expense.user.username)
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    return render(request, 'spese/detail.html', {'page_identification': page_identification,
                                                 'operation': 'show',
                                                 'expense': expense,
                                                }
                 )

                              
@login_required(login_url="/login/")
def change(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    page_identification = 'Spese: edit expense detail'
    sources = Source.objects.filter(users=request.user)
    source_selected = expense.source.pk
    tags_selected = expense.tags.names
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        source_selected = int(request.POST['source'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.source = Source.objects.get(id=source_selected)
                expense.save()
                expense.tags.set(*tags_selected, clear=True)
                expense.save()
                msg = "success modifying expense id {} for user {}".format(expense.id, expense.user.username)
                log.info(msg)
                messages.success(request, msg)
            except:
                # error: Redisplay the expense change form
                msg = 'Error <{}> while trying to change expense {}'.format(sys.exc_info()[0], expense_id)
                log.error(msg)
                messages.error(request, msg)
            else:
                if 'save' in request.POST.keys():
                    return HttpResponseRedirect(reverse('spese:detail', args=(expense.id,)))
    else:
        form = ExpenseForm(instance=expense)
    alltags = Tag.objects.all()
    return render(request, 'spese/add.html', { 'page_identification': page_identification,
                              'operation': 'edit',
                              'form': form,
                              'sources': sources,
                              'source_selected': source_selected,
                              'alltags': alltags,
                              'tags_selected': tags_selected,
                              })

                              
@login_required(login_url="/login/")
def delete(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    try:
        expense.delete()
        msg = "success deleting expense id {} for user {}".format(expense_id, request.user.username)
        log.info(msg)
        messages.success(request, msg)
    except:
        msg = 'Error <{}> while trying to delete expense {}'.format(sys.exc_info()[0], expense_id)
        log.error(msg)
        messages.error(request, msg)
    return HttpResponseRedirect(reverse('spese:index'))

    
