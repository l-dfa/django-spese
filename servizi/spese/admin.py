from django.contrib import admin

from .models import Account, Expense
from .models import WCType, PercentDeduction

admin.site.register(Account)
admin.site.register(Expense)
admin.site.register(WCType)
admin.site.register(PercentDeduction)
