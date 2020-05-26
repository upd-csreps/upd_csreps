from django.shortcuts import render

# Create your views here.

def wip(request):
	context = {}
	return render(request, 'main/wip.html', context)