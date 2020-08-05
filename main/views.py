from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

def wip(request):
	context = {}
	return render(request, 'main/wip.html', context)

def index(request):
	context = {}
	return render(request, 'main/index.html', context)

def wip_redirect(request, exception=None):
	return redirect('main:wip', permanent=True)