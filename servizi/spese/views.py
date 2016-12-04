# spese/views.py
''' app spese views

    ldfa@2016.11.01 changing entity name: from source to account
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
from django.forms import modelform_factory, HiddenInput
from django.utils import timezone
# from django.core.exceptions import ValidationError
# from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

# django authorization
from django.contrib.auth.decorators import login_required

# django models
from django.db import transaction
from django.db.models import Sum
from django.db.models import Q

# spese & taggit
from .models import Expense, Account, WCType, TransferFund
from .forms import ExpenseForm, TransferFundsForm
from .utils import get_accounts
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
    accounts = Account.objects.filter(users=request.user)
    account_selected = None
    tags_selected = []
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        account_selected = int(request.POST['account'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.account = Account.objects.get(id=account_selected)
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
                               'accounts': accounts,
                               'account_selected': account_selected,
                               'alltags': alltags,
                               'tags_selected': tags_selected,
                               })

@login_required(login_url="/login/")
@transaction.atomic
def transfer_funds(request):
    '''     add transfer funds     '''
    page_identification = 'Spese: new transfer funds'
    account_choices = get_accounts(request.user)
    if not account_choices or len(account_choices) < 2:
        msg = 'User {} has too few accounts to do a transfer funds'.format(request.user.username)
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    account_selected = None

    if request.method == "POST":
        form = TransferFundsForm(request.POST, custom_choices=account_choices)
        if form.is_valid():
            try:
                ### TRACE ###                    pdb.set_trace()
                tf_source_id = int(form['tf_source'].value())
                tf_destination_id = int(form['tf_destination'].value())
                expense = form.save(commit=False)
                expense.user = request.user
                expense.account = Account.objects.get(id=tf_source_id)
                expense.save()                                           # setting source record id
                source_id = expense.pk
                # tags = ['transfer_funds']
                # expense.tags.set(*tags, clear=True)                      # (this needs record id)
                expense.save()                                           # this is the complete source record, with tag
                expense.account = Account.objects.get(id=tf_destination_id)
                expense.amount = -expense.amount
                expense.pk = None                                        # https://docs.djangoproject.com/en/1.8/topics/db/queries/#copying-model-instances
                expense.save()                                           # setting destination id
                # expense.tags.set(*tags, clear=True)
                # expense.save()                                           # and this is the destination record
                destination_id = expense.pk
                tfr = TransferFund()
                tfr.source = Expense.objects.get(id=source_id)
                tfr.destination = Expense.objects.get(id=destination_id)
                tfr.save()
                msg =  '{}: success transferring {} funds from {} to {}'.format( expense.user.username,
                                                                                 expense.amount,
                                                                                 tfr.source.account.name,
                                                                                 tfr.destination.account.name
                                                                               )
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
        form = TransferFundsForm(custom_choices=account_choices,
                                 initial={
                                     'description': 'transferring funds',
                                     'date': timezone.now(),
                                 })
        form.fields['work_cost_type'].widget = HiddenInput()
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
    
                 
@login_required(login_url="login/")
def detail(request, expense_id):
    #pdb.set_trace()
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
@transaction.atomic
def change(request, expense_id):
    ''' SVILUPPO il tranfer funds non funziona. VERIFICA:
        - transfer fund: il cambio di account viene impedito
    '''
    expense = get_object_or_404(Expense, pk=expense_id)
    page_identification = 'Spese: edit expense detail'
    accounts = Account.objects.filter(users=request.user)
    account_selected = expense.account.pk
    tags_selected = expense.tags.names
    
    ### TRACE ###    pdb.set_trace()
    other_expense = transfer_fund_get_companion_expense(expense)

    id = expense.id
    oid = other_expense.id if other_expense else None
        
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        account_selected = int(request.POST['account'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                if not other_expense:  expense.account = Account.objects.get(id=account_selected)
                expense.save()
                expense.tags.set(*tags_selected, clear=True)
                expense.save()
                if other_expense:
                    expense.id = other_expense.id
                    expense.account = other_expense.account
                    expense.amount = - expense.amount
                    expense.save()
                    expense.tags.set(*tags_selected, clear=True)
                    expense.save()
                msg = "{}: success modifying expense id {}{}".format( request.user.username, id,
                                                                     " (and companion {})".format(oid) if oid else ""
                                                                   )
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
    if  other_expense:
        messages.info(request, "warning: this is a transfer fund, these changes will affect also its companion")
        messages.info(request, "warning: this is a transfer fund, changes to account will not be accepted")
    return render(request, 'spese/add.html', { 'page_identification': page_identification,
                              'operation': 'edit',
                              'form': form,
                              'accounts': accounts,
                              'account_selected': account_selected,
                              'alltags': alltags,
                              'tags_selected': tags_selected,
                              })

                              
@login_required(login_url="/login/")
@transaction.atomic
def delete(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    other_expense = transfer_fund_get_companion_expense(expense)
    id = expense.id
    oid = other_expense.id if other_expense else None
    try:
        expense.delete()
        if other_expense: other_expense.delete()
        msg = "{}: success deleting expense id {}{}".format( request.user.username, id,
                                                             " (and companion {})".format(oid) if oid else ""
                                                           )
        log.info(msg)
        messages.success(request, msg)
    except:
        msg = 'Error <{}> while trying to delete expense {}'.format(sys.exc_info()[0], expense_id)
        log.error(msg)
        messages.error(request, msg)
    return HttpResponseRedirect(reverse('spese:index'))

    
def transfer_fund_get_companion_expense(expense):
    ''' if expense is a transfer fund, return the "companion" expense '''
    other_expense = None
    tf = TransferFund.objects.filter(source=expense)
    if tf:
        other_expense = tf[0].destination
    else:
        tf = TransferFund.objects.filter(destination=expense)
        if tf: other_expense = tf[0].source
    return other_expense


class RepoItem(object):
    def __init__(self, name, positive, negative, balance):
        self.name = name
        self.positive = positive
        self.negative = negative
        self.balance = balance

    def __str__(self):
        """return name"""
        return self.name


@login_required(login_url='/login/')
def balance(request):
    """ calculates positive, negative and balance sums
        for accounts, tags
    """
    page_identification = 'Spese: Reports'
    list_external_flow_by_account = repo_accounts(request)
    list_internal_flow_by_account = repo_accounts(request, external = False)
    list_external_flow_by_tags = repo_tags(request)
    list_internal_flow_by_tags = repo_tags(request, external = False)
    list_wcts = repo_work_cost_types(request)
    return render(request, 'spese/balance.html', { 'page_identification': page_identification,
                                                   'list_external_flow_by_account': list_external_flow_by_account,
                                                   'list_internal_flow_by_account': list_internal_flow_by_account,
                                                   'list_external_flow_by_tags': list_external_flow_by_tags,
                                                   'list_internal_flow_by_tags': list_internal_flow_by_tags,
                                                   'list_wcts': list_wcts,
                                                 }
                 )

                 
@login_required(login_url='/login/')
def repo_accounts(request, external = True):
    ''' in and out expense by account,
            - regarding EXTERNAL world (NOT transfer funds: external == True)
            - or INTERNAL world (ONLY Transfer Funds: external == False)
    '''
    accounts = Account.objects.filter(users__in=[request.user,])
    list_accounts = []
    total_in  = 0
    total_out = 0
    for item in accounts:
        tfs = TransferFund.objects.values_list('source', flat=True)
        tfd = TransferFund.objects.values_list('destination', flat=True)
        
        sum = Expense.objects.filter(user=request.user, account=item, amount__gt=0)
        sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
        
        sum = Expense.objects.filter(user=request.user, account=item, amount__lt=0)
        sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        item.balance    = item.positive + item.negative
        ri = RepoItem(item.name, item.positive, item.negative, item.balance)
        total_in  += item.positive
        total_out += item.negative
        list_accounts.append(ri)
    rt = RepoItem('totals', total_in, total_out, total_in + total_out)
    list_accounts.append(rt)
    return list_accounts

    
@login_required(login_url='/login/')
def repo_work_cost_types(request):
    """ for every work cost type calculates positive, negative and balance sums """
    wcts = WCType.objects.all()
    list_wcts = []
    total_in  = 0
    total_out = 0
    for item in wcts:
        sum = Expense.objects.filter(user=request.user, work_cost_type=item, amount__gt=0).aggregate(Sum("amount"))
        item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
        sum = Expense.objects.filter(user=request.user, work_cost_type=item, amount__lt=0).aggregate(Sum('amount'))
        item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0
        item.balance    = item.positive + item.negative
        ri = RepoItem(item.name, item.positive, item.negative, item.balance)
        total_in  += item.positive
        total_out += item.negative
        list_wcts.append(ri)
    rt = RepoItem('totals', total_in, total_out, total_in + total_out)
    list_wcts.append(rt)
    return list_wcts
    

@login_required(login_url='/login/')
def repo_tags(request, external = True):
    """ tag by tag calculates positive, negative and balance sums """
    tags = Tag.objects.all()
    list_tags = []
    total_in  = 0
    total_out = 0
    for item in tags:
        tfs = TransferFund.objects.values_list('source', flat=True)
        tfd = TransferFund.objects.values_list('destination', flat=True)

        sum = Expense.objects.filter(user=request.user, tags__in=[item,], amount__gt=0)
        sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        sum = Expense.objects.filter(user=request.user, tags__in=[item,], amount__lt=0)
        sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        item.balance    = item.positive + item.negative
        ri = RepoItem(item.name, item.positive, item.negative, item.balance)
        total_in += item.positive
        total_out += item.negative
        list_tags.append(ri)
    ### TRACE ###    pdb.set_trace()
    wout_tags = Expense.objects.exclude(user=request.user, tags__in=tags)
    sum = wout_tags.filter(amount__gt=0)
    sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
    sum = sum.aggregate(Sum("amount"))
    positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
    log.debug("positive sum: {}".format(sum))

    sum = wout_tags.filter(amount__lt=0)
    sum = sum.exclude(pk__in=tfs).exclude(pk__in=tfd) if(external) else sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
    sum = sum.aggregate(Sum("amount"))
    negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0
    log.debug("negative sum: {}".format(sum))

    total_in += item.positive
    total_out += item.negative
    ri = RepoItem('without tags', positive, negative, positive + negative)
    list_tags.insert(0, ri)
    rt = RepoItem('totals', total_in, total_out, total_in + total_out)
    list_tags.append(rt)
    return list_tags

