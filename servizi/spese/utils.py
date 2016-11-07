#spese/utils.py
''' app spese utils

   ldfa@2016.11.07  chg get_gources in get_accounts
   ldfa@2016.08.09  adding get_sources(request)
'''

# django and app
from django import forms
from .models import Account

def get_accounts(user):
    ''' from user returns
        ((accountid1, accountname1,) (accountid2, accountname2, ) ...)
    '''
    accounts = Account.objects.filter(users=user)
    ids = [(s.id, s.name,) for s in accounts]
    return tuple(ids)

    
