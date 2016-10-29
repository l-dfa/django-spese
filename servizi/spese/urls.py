# spese/urls.py

from django.conf.urls import url
from django.contrib.auth import views as auth_views
# from spese.forms import LoginForm

from . import views

app_name = 'spese'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<expense_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^add/$', views.add, name='add'),
    url(r'^transfer_funds/$', views.transfer_funds, name='transfer_funds'),
    url(r'^balance/$', views.balance, name='balance'),
    url(r'^tags_balance/$', views.tags_balance, name='tags_balance'),
    url(r'^change/(?P<expense_id>[0-9]+)/$', views.change, name='change'),
    url(r'^toggle/(?P<expense_id>[0-9]+)/$', views.toggle, name='toggle'),
    url(r'^delete/(?P<expense_id>[0-9]+)/$', views.delete, name='delete'),
]