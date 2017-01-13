# spese/models.py
''' app spese models
        - ExpenseManager
        - Account,          where to pay for expense
        - Expense
        - WCType,           work cost type
        - PercentDeduction, % to apply in deduction of WCType calculating income tax
        - TransferFund,     collect money tranfer between accounts
'''
# History
# ldfa@2016.12.06 + transferFund.set, + expense.get_companion
#                 and others (playing with "companion" idea)
# ldfa@2016.11.01 changing entity name: from source to account

import datetime
# import pdb 

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# from expense.templatetags import numberformat
from django.db.models import Q
from taggit.managers import TaggableManager       # adding tagging (blog's tagging, not django's)


# class ExpenseManager(models.Manager):
#     """Manager class of Expense objects.
#     
#     This class derive from class *Expense* of *django-expense* app.
#     Please keep note of its copyright @
#     https://django-expense.readthedocs.io/en/latest/license.html
#     """
#     
#     def get_months(self):
#         """Return the list of the months where expense objects are recorded"""
#         
#         return Expense.objects.dates('date', 'month', order='DESC')
# 
#     def get_years(self):
#         """Returns the list of the years where expense objects are recorded"""
#         
#         return Expense.objects.dates('date', 'year', order='DESC')

class Account(models.Model):
    """ This model represents from where to pay for expense
        :Fields:
            * ``name``, the source name;
            * ``users``, who can use this source.
    """
    
    name = models.CharField(_('name'), max_length=50)
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = _('accounts')
        verbose_name = _('account')
        ordering = ['name', ]

    def __str__(self):
        return ("%s" % (self.name))

class Expense(models.Model):
    """ Expenses are represented by this model.
    
        This class derive from class *Expense* of *django-expense* app.
        Please keep note of its copyright @
        https://django-expense.readthedocs.io/en/latest/license.html
    
        :Fields:
            * ``user``,        this is the *owner* of the expense, he is the logged in
                                   user when the new expense is added
            * ``source``,      from where the expense is payed
            * ``date``,        when the expense is payed
            * ``description``, of the expense
            * ``amount``,      of the expense
            * ``tags``,        categorization(s) of the expense; uses django taggit
            
        .. note:: ``null=True`` sets ``NULL`` (versus ``NOT NULL``) on the column in your DB.    
                   Blank values for Django field types such as ``DateTimeField`` or
                   ``ForeignKey`` will be stored as ``NULL`` in the DB.
                   
                   ``blank=True`` determines whether the field will be required in forms.
    """
    user    = models.ForeignKey( User )
    account = models.ForeignKey( Account, related_name='expenses', null=False, default=1 )
    work_cost_type = models.ForeignKey( 'WCType', related_name='work_cost_type', null=True, blank=True )
    date    = models.DateField( _('date'), 'date', default=timezone.now)
    description    = models.TextField( _('description'), max_length=500, null=True,
                                       blank=True
                                     )
    amount  = models.DecimalField( _('amount'), max_digits=8, decimal_places=2 )
    tags    = TaggableManager()

    def get_companion(self):
        ''' if expense is a transfer fund, return the "companion" expense '''
        result = None
        tfq = TransferFund.objects.filter(Q(source=self) | Q(destination=self))
        if tfq: result = tfq[0].destination if tfq[0].source==self else tfq[0].source
        return result
    
    def get_companion_id(self):
        """ if expense is a transfer fund, return the companion expense's id """
        c = self.get_companion()
        return c.id if c else None
    
    def has_companion(self):
        ''' if expense is a transfer fund, return True '''
        tfq = TransferFund.objects.filter(Q(source=self) | Q(destination=self))
        return True  if tfq else False
    
    def delete_with_companion(self):
        with transaction.atomic():
            self.delete_companion()
            self.delete()
        
    def delete_companion(self):
        if self.has_companion():
            c = self.get_companion()
            c.delete()

    class Meta:
        """define verbose name, its plural, and the ordering as -date + account"""
        verbose_name_plural = _('expenses')
        verbose_name = _('expense')
        ordering = ['-date', 'account', ]

    def __str__(self):
        """return description"""
        return '{} - {} @ {}'.format(self.id, self.description, self.date_str())

    def formatted_amount(self):
        """return *amount* as string in css class ``number``"""
        return ('<div class="number">%s</div>' %
                (numberformat.numberformat(self.amount), ))

    # formatted_amount.short_description = _('amount')
    # formatted_amount.allow_tags = True

    def date_str(self):
        """return the date as string formatted by ``%Y-%m-%d`` pattern"""
        return self.date.strftime("%Y-%m-%d")

    date_str.short_description = _("date")

class WCType(models.Model):
    """ Work Cost Types """
    name   = models.CharField(_('name'), max_length=200, null=False, blank=False)
    description = models.TextField(_('description'), max_length=500, null=True, blank=True)
    
    class Meta:
        """define verbose name, its plural, and the ordering """
        verbose_name_plural = _('expense work cost types')
        verbose_name = _('expense work cost type')
        ordering = ['name', ]

    def __str__(self):
        """return name"""
        return '{}'.format(self.name)

def valid_percent(val):
    if val>=0 and val <=1:
       return val
    else:
        raise ValidationError(
              _('%(value)s is not between 0  and 1'),
                params={'value': value},
           )
           
class PercentDeduction(models.Model):
    wc_type = models.ForeignKey(WCType, related_name='wc_ype', null=False, default=1)
    percent     = models.FloatField(_('percent'), validators=[valid_percent])
    valid_from  = models.DateField(_('valid from'), 'valid_from', null=True, blank=True, default=timezone.now)
    valid_to    = models.DateField(_('valid to'), 'valid_to', null=True, blank=True, default=timezone.now)
    
    class Meta:
        """define verbose name, its plural, and the ordering"""
        verbose_name_plural = _('percent deductions')
        verbose_name = _('percent deduction')
        ordering = ['wc_type__name', '-valid_from']

    def __str__(self):
        """return description"""
        return '{} - %:{} from {} to {}'.format(self.wc_type.name,
                                                self.percent,
                                                self.valid_from if self.valid_from!=None else "-",
                                                self.valid_to   if self.valid_to!=None else "-")


class TransferFund(models.Model):
    source = models.OneToOneField(Expense, related_name='source')
    destination = models.OneToOneField(Expense, related_name='destination')
    
    def set(self, expense, account):
        self.source = expense
        with transaction.atomic():
            d = Expense( user=self.source.user,
                         account=account,
                         date=self.source.date,
                         description=self.source.description,
                         amount=-self.source.amount
                       )
            d.save()
            self.destination = d
            self.save()
    
    class Meta:
        """define transfer funds """
        verbose_name_plural = _('transfer funds')
        verbose_name = _('transfer fund')

    def __str__(self):
        """return description"""
        return 'from {} to {} id {} @ {} # {}'.format( self.source.account.name,
                                                 self.destination.account.name,
                                                 self.source.id,
                                                 self.source.date,
                                                 self.source.amount
                                               )
                                                
                                                
