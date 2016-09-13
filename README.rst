=====
Spese
=====

Spese is a simple Django app to register personal expenses,
inspired by `django-expense<https://django-expense.readthedocs.io/en/latest/>`_.  

Detailed documentation will be in the "docs" directory
(not implemented yet).

Quick start
-----------

0. If you have a your project to host spese, use it.
   Otherwise create a base project as follows.
   Install a virtualenv with python 3.5, django, django-taggit, django-spese
   and create the project::

    mkdir progetto_servizi
    cd progetto_servizi
    virtualenv env                                  (this loads a copy of the system's python)
    source env/bin/activate                         (or, in Windows, env\Scripts\activate)
    pip install path/to/django-spese-0.1.tar.gz     (this loads django-spese's
                                                       dependencies: django, django-taggit, ...)
    django-admin startproject servizi

1. Add "spese" and "taggit" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'spese',
        'taggit',
    ]
    
   and check; spese needs these::
     django.contrib.sessions.middleware.SessionMiddleware and
     django.contrib.messages.middleware.MessageMiddleware
     in MIDDLEWARE_CLASSES = [ ... ]

2. Include the spese URLconf in your project urls.py like this::

    from django.conf.urls import include
    ...
    url(r'^spese/', include('spese.urls')),

3. Provide the django login machinery in your project::
   a template/login.html template; in its url.py add::
   
    from django.contrib.auth import views as auth_views
    ...
    url('^login/$', auth_views.login, {'template_name': 'login.html',}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'), 

   and in setting.py add::
   
    LOGIN_REDIRECT_URL = '/' # It means home view
    
   you can copy a login.html example from
   .../env/Lib/site-packages/spese/templates/example/*   (in windows use backslashes)

4. Provide a template/base.html template in your project.
   In base.html the block content marks where spese is
   going to write its contents::
   
    {% block content %}
    {% endblock %}

   you can copy a base.html examples from
   .../env/Lib/site-packages/spese/templates/example/*   (in windows use backslashes)

5. Run `python manage.py migrate` to create the spese models and
   adding a minimal dataset: user1, user2, transfer_funds tag, 
   and cache source for user1 and user2.

6. Run `python manage.py createsuperuser` to create a superuser.

7. Start the development server (python manage.py runserver) 
   and visit http://127.0.0.1:8000/admin/ ,
   login as superuser to add/change/delete DB base items: sources, tags, users.
   (and expenses. But furnish a user interface to accomplish this
   task is one target of spese app).
   
   you'll need the Admin app enabled

8. Visit http://127.0.0.1:8000/spese/ , login as a user and enjoi the app.