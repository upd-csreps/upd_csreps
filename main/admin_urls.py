from django.urls import path

from . import views as main
from troubleshooter import views as troubleshooter

app_name = 'admin'

urlpatterns = [
    path('', main.admin, name='index'),
    path('troubleshooter/', troubleshooter.admin , name='troubleshooter'),
]