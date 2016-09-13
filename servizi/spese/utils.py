#spese/utils.py
''' app spese utils

   ldfa@2016.08.09  adding get_sources(request)
'''

# django and app
from django import forms
from .models import Source

def get_sources(user):
    ''' from user returns
        ((sourceid1, sourcename1,) (sourceid2, sourcename2, ) ...)
    '''
    sources = Source.objects.filter(users=user)
    ids = [(s.id, s.name,) for s in sources]
    return tuple(ids)

    
