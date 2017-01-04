# servizi/views.py
# from django.http import HttpResponse
from django.shortcuts import render
#from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from .last_commit_id import commit_id

@login_required(login_url="login/")
def home(request):
    # return HttpResponse("Hello, world. You're at the servizi index.")
    user = request.user
    return render(request, 'home.html', { 'user': user, 'commit_id': commit_id} )