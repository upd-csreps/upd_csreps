from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('', views.wip, name='wip'),
    path('index/', views.index, name='index'),
]