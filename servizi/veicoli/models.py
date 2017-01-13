# veicoli/models.py
#{ module history
#    ldfa@2017.01.11 + unique option in VType, VEvent & Vehicle name fields
#}
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# from expense.templatetags import numberformat
from django.db.models import Q

from spese.models import Expense

class VType(models.Model):
    """ Vehicle type representation
        :Fields:
            * ``name``,        v.type name (examples: car, motorcycle, aeroplane, starship, ...);
            * ``description``, its description;
    """
    
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.CharField(_('description'), max_length=250)

    class Meta:
        verbose_name_plural = _('VTypes')
        verbose_name = _('vehicle type')
        ordering = ['name', ]

    def __str__(self):
        return ("%s" % (self.name))
        
class VEvent(models.Model):
    """ Vehicle event type
        :Fields:
            * ``name``,        event type name (examples: fuel, maintenance, ...)
            * ``description``, its description.
    """
    
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.CharField(_('description'), max_length=250)

    class Meta:
        verbose_name_plural = _('VEvents')
        verbose_name = _('vehicle event')
        ordering = ['name', ]

    def __str__(self):
        return ("%s" % (self.name))
        
class Vehicle(models.Model):
    """ Vehicle representation
        :Fields:
            * ``users``,     (a ref.to) who can use this vehicle.
            * ``name``,      the v.name;
            * ``type``,      (a ref.to) the v.type (VType)
            * ``description``, v.description
            * ``start``,     v.availability start date
            * ``end``,       and v. availability end date (if None, now available)
    """
    
    user = models.ForeignKey(User)
    name = models.CharField(_('name'), max_length=50, unique=True)
    type = models.ForeignKey(VType)
    description = models.CharField(_('description'), max_length=250)
    start = models.DateField(_('start'), 'start', null=True, blank=True, default=timezone.now)
    end   = models.DateField(_('end'),   'end',   null=True, blank=True)

    class Meta:
        verbose_name_plural = _('vehicles')
        verbose_name = _('vehicle')
        ordering = ['name', ]

    def __str__(self):
        return ("%s" % (self.name))
        
class Event(models.Model):
    """ Event representation
        :Fields:
            * ``expense``, link to expense;
            * ``vehicle``, link to vehicle;
            * ``vevent``,  link to event type;
            * ``km``,      at what distance it occured;
            * ``unit_cost``, how much costs the unit of the acquired item
                             usually for refuelling events; i.e. €/l
    """
    
    expense = models.OneToOneField(Expense)
    vehicle = models.ForeignKey(Vehicle)
    vevent = models.ForeignKey(VEvent)
    km = models.PositiveIntegerField(_('km'))
    unit_cost = models.DecimalField(_('unit_cost'), null=True, max_digits=8, decimal_places=3)

    class Meta:
        verbose_name_plural = _('events')
        verbose_name = _('event')
        ordering = ['expense', ]

    def __str__(self):
        return ("%s" % (self.expense))