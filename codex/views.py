from django.shortcuts import render

# Create your views here.
def index(request, exception=None):
	context = {}
	return render(request, 'main/wip.html', context)