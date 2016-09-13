# servizi/views.py
# from django.http import HttpResponse
from django.shortcuts import render
#from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

@login_required(login_url="login/")
def home(request):
    # return HttpResponse("Hello, world. You're at the servizi index.")
    return render(request, 'home.html')