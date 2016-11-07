# spese/models.py
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# from expense.templatetags import numberformat
from django.db.models import Q
from taggit.managers import TaggableManager                       # adding tagging (blog's tagging, not django's)


class ExpenseManager(models.Manager):
    """Manager class of Expense objects.
    
    This class derive from class *Expense* of *django-expense* app.
    Please keep note of its copyright @
    https://django-expense.readthedocs.io/en/latest/license.html
    """
    
    def get_months(self):
        """Return the list of the months where expense objects are recorded"""
        
        return Expense.objects.dates('date', 'month', order='DESC')

    def get_years(self):
        """Returns the list of the years where expense objects are recorded"""
        
        return Expense.objects.dates('date', 'year', order='DESC')

class Account(models.Model):
    """ From where to pay for expense is represented by this model
    
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
    
    * ``user``, this is the *owner* of the expense, he is the logged in
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
    
    user = models.ForeignKey(User)
    account = models.ForeignKey(Account, related_name='expenses', null=True,
                               blank=True, default=1)
    date = models.DateField(_('date'), 'date', null=True, blank=True, default=timezone.now)
    description = models.CharField(_('description'), max_length=300, null=True,
                               blank=True)
    amount = models.DecimalField(_('amount'), max_digits=8, decimal_places=2)

    tags = TaggableManager()

    class Meta:
        """define verbose name, its plural, and the ordering as -date + account"""
        verbose_name_plural = _('expenses')
        verbose_name = _('expense')
        ordering = ['-date', 'account', ]

    def __str__(self):
        """return description"""
        return self.description

    def formatted_amount(self):
        """return *amount* as string in css class ``number``"""
        return ('<div class="number">%s</div>' %
                (numberformat.numberformat(self.amount), ))

    formatted_amount.short_description = _('amount')
    formatted_amount.allow_tags = True

    def date_str(self):
        """return the date as string formatted by ``%Y-%m-%d`` pattern"""
        return self.date.strftime("%Y-%m-%d")

    date_str.short_description = _("date")

