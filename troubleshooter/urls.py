from django.urls import path

from . import views

app_name = 'troubleshooter'
urlpatterns = [
    path('', views.index, name='index'),
]