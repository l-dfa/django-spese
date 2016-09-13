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
    """
    Manager class of Expense objects.
    """
    def get_months(self):
        """
        Return the list of the months where expense objects are
        recorded.
        """
        return Expense.objects.dates('date', 'month', order='DESC')

    def get_years(self):
        """
        Returns the list of the where expense objects are
        recorded.
        """
        return Expense.objects.dates('date', 'year', order='DESC')

class Source(models.Model):
    """
    From where to pay for expense is represented by this model.
    """
    name = models.CharField(_('name'), max_length=50)
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = _('sources')
        verbose_name = _('source')
        ordering = ['name', ]

    def __str__(self):
        return ("%s" % (self.name))


class Expense(models.Model):
    """
    Expenses are represented by this model.
    Remember: null=True sets NULL (versus NOT NULL) on the column in your DB.
              Blank values for Django field types such as DateTimeField or
              ForeignKey will be stored as NULL in the DB.
              blank=True determines whether the field will be required in forms.
    Fields: user,        this is the "owner" of the expense, he is the logged in
                         user when the new expense is added
            source,      from where the expense is payed
            date,        when the expense is payed
            description, of the expense
            amount,      of the expense
            tags,        categorization(s) of the expense; uses django taggit
    """
    user = models.ForeignKey(User)
    source = models.ForeignKey(Source, related_name='expenses', null=True,
                               blank=True, default=1)
    date = models.DateField(_('date'), 'date', null=True, blank=True, default=timezone.now)
    description = models.CharField(_('description'), max_length=300, null=True,
                               blank=True)
    amount = models.DecimalField(_('amount'), max_digits=8, decimal_places=2)
    # objects = ExpenseManager()
    # date.expense_date_filter = True

    tags = TaggableManager()

    class Meta:
        verbose_name_plural = _('expenses')
        verbose_name = _('expense')
        # ordering = ['-date', 'category__type__name', 'category__name']
        ordering = ['-date', 'source', ]

    def __str__(self):
        return self.description

    def formatted_amount(self):
        return ('<div class="number">%s</div>' %
                (numberformat.numberformat(self.amount), ))

    formatted_amount.short_description = _('amount')
    formatted_amount.allow_tags = True

    def date_str(self):
        """
        Formats the date by "%Y-%m-%d." pattern.
        """
        return self.date.strftime("%Y-%m-%d")

    date_str.short_description = _("date")

