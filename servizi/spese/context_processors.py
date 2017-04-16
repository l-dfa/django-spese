from django.conf import settings # import the settings file

def commit_id(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'COMMIT_ID': settings.COMMIT_ID}