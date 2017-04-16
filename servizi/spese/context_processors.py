from django.conf import settings # import the settings file

def commit_ver(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'COMMIT_VER': settings.COMMIT_VER}