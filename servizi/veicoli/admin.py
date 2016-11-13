from django.contrib import admin

from .models import VType, VEvent, Vehicle, Event

admin.site.register(VType)
admin.site.register(VEvent)
admin.site.register(Vehicle)
admin.site.register(Event)