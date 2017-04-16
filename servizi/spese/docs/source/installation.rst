.. _installation:

Installation
============

To install *django-spese*, you'll need some prerequisite:

* first of all you must know how type commands in console mode in
  your system;
* then, it's important you have some knowledge about how create/configure
  a Django project and app(s);
* and, last but not least, you'll need to have a copy of
  `Python <https://www.python.org/>`_ version 3.5, or newer, already installed
  in your system.  

Futhermore I take for granted you know how to use virtualenv
and you'll use it to create a Django project to test this app.

Hereafter I describe how install from a distribution. You can download it from `this tar.gz
<https://github.com/l-dfa/django-spese/releases/download/v0.5/django-spese-0.5.tar.gz>`_ ,
or from `this zip archive
<https://github.com/l-dfa/django-spese/releases/download/v0.5/django-spese-0.5.zip>`_ 
if you prefer a zipped version.

.. note:: If you are a developer, maybe you'd like to clone from the
  `project source repository <https://github.com/l-dfa/django-spese>`_ 
  using `git <https://git-scm.com/>`_ as version control software.

Creating a Django project to host the application
-------------------------------------------------

If you have your project to host *django-spese*, use it, and go to `Configuring the project`_.

Otherwise create a base project using virtualenv as follows::

    > mkdir progetto_servizi
    > cd progetto_servizi
    > virtualenv env                                  (this loads a copy of the system's python)
    > source env/bin/activate                         (or, in Windows, env\Scripts\activate)
    > pip install path/to/django-spese-0.1.tar.gz     (this loads django-spese and its
                                                       dependencies: django, django-taggit, ...)

then and create the django project::

    > django-admin startproject servizi

Configuring the project
-----------------------

Add *django-spese* and *taggit* to your ``INSTALLED_APPS`` in ``setting.py``. Like this::

    INSTALLED_APPS = [
        ...
        'spese',
        'taggit',
    ]
    
And, again in ``settings.py`` double check the presence of:
   
*    ``django.contrib.sessions.middleware.SessionMiddleware`` and
*     ``django.contrib.messages.middleware.MessageMiddleware``

in ``MIDDLEWARE_CLASSES = [ ... ]``

Include the *django-spese* URLconf in your project ``urls.py``. Like this::

    from django.conf.urls import include
    ...
    url(r'^spese/', include('spese.urls', namespace='spese')),

Provide the django login machinery in your project: that is 
a ``template/login.html`` template, in your project ``url.py`` add::
   
    from django.contrib.auth import views as auth_views
    ...
    url('^login/$', auth_views.login, {'template_name': 'login.html',}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'), 

and in ``setting.py`` add::
   
    LOGIN_REDIRECT_URL = '/' # It means home view
    
You can copy a ``login.html`` example from
``.../env/Lib/site-packages/spese/templates/example/*``   (in windows use backslashes)

Provide a ``template/base.html`` template in your project.
In ``base.html`` the block ``content`` marks where *django-spese* is
going to write its contents::
   
    {% block content %}
    {% endblock %}

You can copy a ``base.html`` examples from
``.../env/Lib/site-packages/spese/templates/example/*``   (in windows use backslashes)

Creating the database
---------------------

Run ``python manage.py migrate`` to create the *django-spese* models and
adding a minimal dataset: *user1*, *user2*, *transfer_funds* tag, 
and *cache* source for *user1* and *user2*.

Run ``python manage.py createsuperuser`` to create a *superuser*.

Start the development server (``python manage.py runserver``) 

Refining the database contents
------------------------------

Visit http://127.0.0.1:8000/admin/ .

Login as *superuser* to add/change/delete DB base items: sources, tags, users
(... and expenses. But furnish a user interface to accomplish this
task is one target of spese app).
   
.. note:: you'll need the *Admin* app enabled

.. note:: As superuser, at least, reset the users *user1* and *user2* passwords
          at known values.
          
          It might be a good idea to change the user names to something more
          meaningful too.

Enjoi
-----

Visit http://127.0.0.1:8000/spese/ , login as a user and enjoi the app.
