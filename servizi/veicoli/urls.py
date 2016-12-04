# veicoli/urls.py

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'veicoli'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<expense_id>\d+)$', views.detail, name='detail'),
    url(r'^add/$', views.add, name='add'),
    url(r'^change/(?P<expense_id>[0-9]+)/$', views.change, name='change'),
]