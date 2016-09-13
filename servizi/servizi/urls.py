# servizi/urls.py
"""servizi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from . import views
# from .forms import LoginForm

urlpatterns = [
    url(r'^$', views.home, name='home'),              # servizi index
    url(r'^home$', views.home, name='home'),          # servizi index
    url(r'^spese/', include('spese.urls')),
    url(r'^admin/', admin.site.urls),
    # url('^login/$', auth_views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url('^login/$', auth_views.login, {'template_name': 'login.html',}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'), 
]
