# spese/views.py
''' app spese views:
        - toggle(id), change amount sign
        - add,        create new expense
        - transfer_funds, create new transfer fund
        - index,      list all expenses summary
        - detail(id), show expense detail
        - change(id), change expense
        - delete(id), delete expense
        - balance,    reports by accounts, tags, ...
            - repo_accounts
            - repo_work_cost_types
            - repo_tags
'''
#{ module history  (notepad users: cursor prev.curly bracket, then ctrl+alt+b to highlight, alt+h to hide)
#    ldfa@2017.04.14 filters.py: + "not_for_work" & "description" filter fields
#                    +export_csv: export current expenses list to csv file
#    ldfa@2017.01.13 RepoItem: balance calculated in object instantiation instead
#                              of a parameter passing
#                    repo_accounts, repo_work_cost_types, repo_tags: commented out @login_required
#                               becouse these are module internal functions
#    ldfa@2017.01.11 index:    chg passing request to django-filter to select
#                              the applicable account
#                    balance:  + account & date filters by django-filter
#    ldfa@2017.01.04 index:  + account & date filters by django-filter
#    ldfa@2016.12.12 toggle: + check request user against expense user
#                    detail: + check request user against expense user
#                    change: + check request user against expense user
#                    delete: + check request user against expense user
#    ldfa@2016.12.06 using transferFund.set, expense.get_companion
#    ldfa@2016.12.04 using transaction.atomic
#                    better reporting (splitted external flow from transfer funds)
#    ldfa@2016.11.01 changing entity name: from source to account
#    ldfa@2016.10.29 adding log facility in primary program points
#        bug 0001: got a pdb error in transfer funds from production site.
#                  after introducing the log facility it doesn't appair again.
#                  it seems as I forgot a pdb.set_trace on. but it isn't in repository,
#    ldfa@2016.09.11 added a project css:
#           - servizi/static/css/servizi.css:  project specific css attributes
#        reduced h1 height in servizi.css 
#        added a page_identification block in base.html feeded from apps
#    ldfa@2016.09.07-11  fighting to deploy the project to my production server
#        releasing python+virtualenv+django in a centos 6+apache framework
#        via mod_wsgi was harder than I aspected. However finally it worked!
#    ldfa@...-2016.08.14 moving some css from project to app:
#           - spese/static/spese/spese.css;   spese specific css attributes 
#           - /servizi/template/base.html:    added {% block stylesheet %} 
#           - spese/template/spese/*.html:    added {% load staticfiles %} and stylesheet block
#        right justified the amount column in spese/template/spese/index.html
#        adopted the css skeleton boilerplate (http://getskeleton.com/)
#           modified spese/template/spese/*.html and /servizi/template/css/*.hmtl
#        visual adjustments of User Interface
#    ldfa@2016.08.08 moving login from app to project:
#            - /servizi/templates/login.html; login template
#            - /servizi/servizi/forms.py;     contains class LoginForm 
#            - login_url="/login/";           project url (...="login/" would kept hostname/spes/login)
#}


import csv
import pdb                              # python debugging
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
from .filters import ExpenseFilter
from .utils import get_accounts
from taggit.models import Tag


@login_required(login_url="/login/")
def toggle(request, expense_id):
    ''' change amount sign '''
    expense = get_object_or_404(Expense, pk=expense_id)
    # check expense user == request user, othewise bail out
    if expense.user != request.user:
        msg = "{}: access to expense id {} denied".format( request.user.username, expense.pk )
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    
    error = False
    try:
        expense.amount = -expense.amount
        expense.save()
        msg = "success toggling expense id {} for user {}".format(expense.id, expense.user.username)
    except:
        msg = 'Error <{}> while toggling expense {}'.format(sys.exc_info()[0], expense_id)
        error = True
    log.info(msg) if not error else log.error(msg)
    messages.success(request, msg) if not error else messages.error(request, msg)
    return HttpResponseRedirect(reverse('spese:detail', args=(expense.id,)))
                             

@login_required(login_url="/login/")
def add(request):
    ''' create new expense '''
    page_identification = 'Spese: new expense'
    accounts = Account.objects.filter(users=request.user)
    account_selected = None
    tags_selected = []
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        account_selected = int(request.POST['account'])
        tags_selected = request.POST.getlist('choice')                 # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                with transaction.atomic():
                    expense = form.save(commit = False)                # creates new expense not saved in DB
                    expense.user = request.user
                    expense.account = Account.objects.get(id=account_selected)
                    expense.save()                                     # save new expense to DB (this set expense.pk)
                    # managing tags; this is a different step because it's a m:n relationship
                    tags = request.POST.getlist('choice')              ## gets [] in case of no choices
                    expense.tags.set(*tags, clear=True)                # set tags (clearing the old ones)
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
                if 'save' in request.POST.keys():
                    # SAVE button: jump to show detail of new expense
                    return HttpResponseRedirect(reverse('spese:detail', args=(expense.id,)))
                # SAVE & CONTINUE button: display again the form, with fields already loaded 
    else:
        # first display of the form
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
                                             }
                 )


@login_required(login_url="/login/")
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
                with transaction.atomic():
                    expense = form.save(commit=False)                        # new expense: source account, no id
                    expense.user = request.user
                    expense.account = Account.objects.get(id=tf_source_id)
                    expense.save()                                           # save to DB (got record id)
                    tfr = TransferFund()
                    tfr.set(expense, Account.objects.get(id=tf_destination_id))
                msg =  '{}: success transferring {} funds from {} to {}'.format( expense.user.username,
                                                                                 expense.amount,
                                                                                 tfr.source.account.name,
                                                                                 tfr.destination.account.name
                                                                               )
                log.info(msg)
                messages.success(request, msg)
            except:
                msg = 'Error <{}> while trying to transfer funds'.format(sys.exc_info()[0])
                log.error(msg)
                messages.error(request, msg)
            else:
                # success: back to index
                return HttpResponseRedirect(reverse('spese:index'))
            # error: Redisplay the expense change form
    else:
        # first load of form
        form = TransferFundsForm(custom_choices=account_choices,
                                 initial={
                                     'description': 'transferring funds',
                                     'date': timezone.now(),
                                 })
        form.fields['work_cost_type'].widget = HiddenInput()   # transfer funds haven't work cost type
    return render(request, 'spese/transfer_funds.html', {'page_identification': page_identification,
                                                         'operation': 'add',
                                                         'form': form,
                                                        }
                 )

                              
@login_required(login_url='/login/')
def index(request):
    page_identification = 'Spese'
    ### TRACE ###     pdb.set_trace()
    e_l = ExpenseFilter(request.GET, request=request, queryset=Expense.objects.filter(user=request.user))   # expenses_list
    request.session['filter_data'] = e_l.data
    return render(request, 'spese/index.html', { 'page_identification': page_identification,
                                                 'expenses_list': e_l,
                                               }
                 )    

@login_required(login_url="/login/")
def export_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    filter_data = request.session.get('filter_data')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_list.csv"'

    e_l = ExpenseFilter(filter_data, request=request, queryset=Expense.objects.filter(user=request.user))   # expenses_list
    # pdb.set_trace()
    writer = csv.writer(response)
    for row in e_l.qs:
        writer.writerow([row.pk, row.account.name, row.work_cost_type.name if row.work_cost_type else '', row.date, row.description, row.amount])

    return response
    
                 
@login_required(login_url="login/")
def detail(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    # check expense user == request user, othewise bail out
    if expense.user != request.user:
        msg = "{}: access to expense id {} denied".format( request.user.username, expense.pk )
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    
    page_identification = 'Spese: show expense detail'
    other_expense = expense.get_companion()   # if expense is a transfer fund, this gets its companion
    
    # if not expense.user == request.user:
    #     msg = "expense id {}: wrong user (it's {})".format(expense.id, expense.user.username)
    #     log.error(msg)
    #     messages.error(request, msg)
    #     return HttpResponseRedirect(reverse('spese:index'))
    if other_expense:
        ###TRACE ### pdb.set_trace()
        other_url = reverse('spese:detail', kwargs={'expense_id': str(other_expense.pk)})
        messages.info( request,
                       'this is a transfer fund bound to <a href="{}">this one</a> in "{}" account'.format(other_url, other_expense.account.name),
                       extra_tags='safe'
                     )
    return render(request, 'spese/detail.html', {'page_identification': page_identification,
                                                 'operation': 'show',
                                                 'expense': expense,
                                                }
                 )

                              
@login_required(login_url="/login/")
def change(request, expense_id):
    ''' be aware: this one changes every kind of expense; even transfer funds
        in case of transfer funds:
            - cannot change account in companion expense
            - changes description, date and amount in companion expense
    '''
    expense = get_object_or_404(Expense, pk=expense_id)
    # check expense user == request user, othewise bail out
    if expense.user != request.user:
        msg = "{}: access to expense id {} denied".format( request.user.username, expense.pk )
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    
    page_identification = 'Spese: edit expense detail'
    accounts = Account.objects.filter(users=request.user)
    account_selected = expense.account.pk
    tags_selected = expense.tags.names
    
    ### TRACE ###    pdb.set_trace()
    other_expense = expense.get_companion()   # if expense is a transfer fund, it gets its companion

    id = expense.id
    oid = other_expense.id if other_expense else None
        
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        account_selected = int(request.POST['account'])
        tags_selected = request.POST.getlist('choice')   # 'getlist' gets [] in case of no choices
        if form.is_valid():
            try:
                with transaction.atomic():
                    expense = form.save(commit=False)      # this has id because ExpenseForm(..., instance=expense)
                    if not other_expense:  expense.account = Account.objects.get(id=account_selected)
                    expense.save()
                    # as usual for tags: another step because of m:n relationship
                    expense.tags.set(*tags_selected, clear=True)
                    expense.save()
                    if other_expense:                      # if transfer fund, we change even the companion expense
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
        messages.info(request, "warning: this is a transfer fund; these changes will affect also its companion, on {} account".format(other_expense.account.name))
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
def delete(request, expense_id):
    ''' delete expense.
        in case of transfer fund, it deletes source expense,
        destination expense, and record in TransferFund table
    '''
    expense = get_object_or_404(Expense, pk=expense_id)
    # check expense user == request user, othewise bail out
    if expense.user != request.user:
        msg = "{}: access to expense id {} denied".format( request.user.username, expense.pk )
        log.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('spese:index'))
    
    oid = expense.get_companion_id()
    id = expense.id
    try:
        expense.delete_with_companion()
        # with transaction.atomic():
        #     expense.delete_companion()
        #     expense.delete()
        #     if other_expense: other_expense.delete()
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

    

class RepoItem(object):
    def __init__(self, name, positive, negative, int_positive=0, int_negative=0):
        self.name     = name
        self.positive = positive
        self.int_positive = int_positive
        self.int_negative = int_negative
        self.negative = negative
        self.balance  = self.positive + self.int_positive + self.int_negative + self.negative

    def __str__(self):
        """return name and balance"""
        return "{}: {}".format(self.name, self.balance)


@login_required(login_url='/login/')
def balance(request):
    """ calculates positive, negative and balance sums
        for accounts, tags, work cost types
    """
    page_identification = 'Spese: Reports'
    e_l = ExpenseFilter(request.GET, request=request, queryset=Expense.objects.filter(user=request.user))   # expenses_list

    list_external_flow_by_account = repo_accounts(e_l)
    list_external_flow_by_tags = repo_tags(e_l)
    list_wcts = repo_work_cost_types(e_l)
    
    return render(request, 'spese/balance.html', { 'page_identification': page_identification,
                                                   'list_external_flow_by_account': list_external_flow_by_account,
                                                   'list_external_flow_by_tags': list_external_flow_by_tags,
                                                   'list_wcts': list_wcts,
                                                   'expenses_list': e_l,
                                                 }
                 )

                 
# @login_required(login_url='/login/')
def repo_accounts(el):
    ''' in and out expense by account,
            - el,     expenses (query)list
    '''
    #accounts = Account.objects.filter(users__in=[request.user,])
    accounts = [e.account for e in el.qs]
    accounts = list(set(accounts))
    # pdb.set_trace()
    list_accounts = []
    total_in  = 0
    total_out = 0
    for item in accounts:
        tfs = TransferFund.objects.values_list('source', flat=True)
        tfd = TransferFund.objects.values_list('destination', flat=True)
        
        # get income (>0)
        #start_sum = Expense.objects.filter(user=request.user, account=item, amount__gt=0)
        start_sum = el.qs.filter(account=item, amount__gt=0)
        # external input
        sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
        sum = sum.aggregate(Sum("amount"))
        item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        # internal input
        sum = start_sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.int_positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
        
        # geto outcome (<0)
        #start_sum = Expense.objects.filter(user=request.user, account=item, amount__lt=0)
        start_sum = el.qs.filter(account=item, amount__lt=0)
        # internal output
        sum = start_sum.filter(Q(pk__in=tfs) | Q(pk__in=tfd))
        sum = sum.aggregate(Sum("amount"))
        item.int_negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        # external output
        sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
        sum = sum.aggregate(Sum("amount"))
        item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        #item.balance    = item.positive + item.int_positive + item.int_negative + item.negative
        ri = RepoItem(item.name, item.positive, item.negative, int_positive=item.int_positive, int_negative=item.int_negative, )
        total_in  += item.positive
        total_out += item.negative
        list_accounts.append(ri)
    rt = RepoItem('totals', total_in, total_out)
    list_accounts.append(rt)
    return list_accounts

    
# @login_required(login_url='/login/')
def repo_work_cost_types(el):
    """ for every work cost type calculates positive, negative and balance sums """
    #wcts = WCType.objects.all()
    wcts = [e.work_cost_type for e in el.qs]
    wcts = [w for w in wcts if w ]
    ### TRACE ###    pdb.set_trace()
    wcts = list(set(wcts))

    list_wcts = []
    total_in  = 0
    total_out = 0
    if wcts:
        for item in wcts:
            sum = el.qs.filter(work_cost_type=item, amount__gt=0).aggregate(Sum("amount"))
            item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
            sum = el.qs.filter(work_cost_type=item, amount__lt=0).aggregate(Sum('amount'))
            item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0
            # item.balance    = item.positive + item.negative
            ri = RepoItem(item.name, item.positive, item.negative)
            total_in  += item.positive
            total_out += item.negative
            list_wcts.append(ri)
        rt = RepoItem('totals', total_in, total_out)
        list_wcts.append(rt)
    return list_wcts
    

def flatten(qs):
    """Given a queryset, return it flattened.
       this is inspired from
       http://code.activestate.com/recipes/578948-flattening-an-arbitrarily-nested-list-in-python/
    """
    aqs = Account.objects.all()
    new_lis = []
    for item in qs:
        if type(item) == type(aqs):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis
    
# @login_required(login_url='/login/')
def repo_tags(el):
    """ tag by tag calculates positive, negative and balance sums """
    # tags = Tag.objects.all()
    tags = [e.tags.all() for e in el.qs]
    ### TRACE ###    pdb.set_trace()
    tags = flatten(tags)
    tags = list(set(tags))

    list_tags = []
    total_in  = 0
    total_out = 0
    tfs = TransferFund.objects.values_list('source', flat=True)
    tfd = TransferFund.objects.values_list('destination', flat=True)
    for item in tags:

        # get tagged income (>0)
        ### TRACE ### pdb.set_trace()
        start_sum = el.qs.filter(tags__in=[item,], amount__gt=0)
        
        # external income
        sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
        sum = sum.aggregate(Sum("amount"))
        item.positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0

        # get tagged outcome
        start_sum = el.qs.filter(tags__in=[item,], amount__lt=0)
        
        # external tagged outcome
        sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
        sum = sum.aggregate(Sum("amount"))
        item.negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0
                
        # item.balance    = item.positive + item.int_positive + item.int_negative + item.negative
        # ri = RepoItem(item.name, item.positive, item.negative, item.balance, int_positive=item.int_positive, int_negative=item.int_negative)
        # item.balance    = item.positive + item.negative
        ri = RepoItem(item.name, item.positive, item.negative)
        total_in  += item.positive
        total_out += item.negative
        list_tags.append(ri)
    ### TRACE ###    pdb.set_trace()
    
    # get not tagged income
    wout_tags = el.qs.exclude(tags__in=tags)
    start_sum = wout_tags.filter(amount__gt=0)
    
    # external not tagged income
    sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
    sum = sum.aggregate(Sum("amount"))
    positive = sum["amount__sum"] if sum and sum["amount__sum"] else 0
    log.debug("positive sum: {}".format(sum))

    # get not tagged outcome
    start_sum = wout_tags.filter(amount__lt=0)
    
    # external not tagged outcome
    sum = start_sum.exclude(pk__in=tfs).exclude(pk__in=tfd)
    sum = sum.aggregate(Sum("amount"))
    negative = sum["amount__sum"] if sum and sum["amount__sum"] else 0
    log.debug("negative sum: {}".format(sum))
    
    total_in += positive
    total_out += negative
    # balance = positive + int_positive + int_negative + negative
    # ri = RepoItem('without tags', positive, negative, balance, int_positive=int_positive, int_negative=int_negative )
    # balance = positive + negative
    ri = RepoItem('without tags', positive, negative)
    list_tags.insert(0, ri)
    rt = RepoItem('totals', total_in, total_out)
    list_tags.append(rt)
    return list_tags

