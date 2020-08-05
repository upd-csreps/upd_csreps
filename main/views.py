from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

def wip(request):
	context = {}
	return render(request, 'main/wip.html', context)

def wip_redirect(request, exception=None):
	return redirect(reverse('main:wip'), permanent=True)