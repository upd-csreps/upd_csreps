from django.urls import resolve
def appname(request):
    return {'app_name': resolve(request.path).app_name}