from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings

import requests

# Create your views here.

def wip(request):
	context = {}
	return render(request, 'main/wip.html', context)

def index(request):

	fb_url ='https://graph.facebook.com/v8.0/%s/posts' % 'up.csreps'

	parameters = {
		'fields': 'id,attachments',
		'access_token': settings.FB_ACCESS_TOKEN, 
		'limit': 10
	}
	r = requests.get(fb_url, params=parameters)

	context = {}
	return render(request, 'main/index.html', context)

def wip_redirect(request, exception=None):
	return redirect('main:wip', permanent=True)