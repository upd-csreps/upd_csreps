from django.conf import settings
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
import iso8601
import re
import requests

# Create your views here.

@login_required
def admin(request):
	context = {}
	return render(request, 'main/admin.html', context)

def log_in(request):
	if request.method == 'GET':
		if request.user.is_anonymous:
			context = {}
			return render(request, 'main/login.html', context)
		else:
			return redirect('admin:index')
	else:
		data = request.POST

		required_fields = ['usermail', 'password']
		required_complete = True

		for field in required_fields:
			if not (data.get(field, None)):
				required_complete = False
				break

		if required_complete:
			user = User.objects.filter(email=data['usermail'].strip()).first()
			username = data['usermail'].strip()
			print(user)
			if user:
				username = user.username
			user = authenticate(request, username=username, password=data['password'])

			if user:
				login(request, user)

		return redirect('main:login')

def log_out(request):
	if request.user.is_authenticated:
		logout(request)
	return redirect('main:index')


def wip(request, exception=None):
	context = {}
	return render(request, 'main/wip.html', context)

def index(request):
	if request.method == 'GET':
		context = {}
		return render(request, 'main/index.html', context)
	elif request.method == 'POST':
		hlink_regex = "(?:^|\b|\s)((?:([A-Za-z][A-Za-z0-9+.-]*):)?(?:\/\/)?(?:([-A-Za-z0-9_'](?:(?:\.?(?:[-A-Za-z0-9_'~]|%[A-Fa-f]{2}))*[-A-Za-z0-9_'])?)(?::((?:[-A-Za-z0-9_'~!$&()\*+,;=]|%[A-Fa-f]{2})*))@)?((?:localhost)|(?:(?:1?[0-9]{1,2}|2[0-5]{1,2})(?:\.(?:1?[0-9]{1,2}|2[0-5]{1,2})){3})|(?:\[(?:[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)+\])|(?:[A-Za-z0-9](?:(?:\.?[-A-Za-z0-9])*[A-Za-z0-9])?\.[A-Za-z](?:[-A-Za-z0-9]*[A-Za-z0-9])?))(?::[0-9]+)?((?:\/(?:[-A-Za-z0-9._~:@!$&'()*+,;=]|%[A-Fa-f]{2})+)*\/?)(\?(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?(#(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?)(?:\b|\s|$)"
		hashtag_rgx = "(?:^|\b|\s)(#[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*)(?:\b|\s|$)"
		fb_url ='https://graph.facebook.com/v8.0/%s/posts' % 'up.csreps'

		parameters = {
			'fields': 'id,attachments,created_time',
			'access_token': settings.FB_ACCESS_TOKEN, 
			'limit': 10
		}
		r = requests.get(fb_url, params=parameters)

		fb_content = []

		for item in r.json()['data']:
			added = item['attachments']['data'][0]
			added['date'] = iso8601.parse_date(item['created_time'])
			if added['type'] == 'photo':

				tag_list = []
				hashtags = re.findall( hashtag_rgx, added['description'])
				for tags in hashtags:
					tag_list.append(tags[1:])
					added['description'] = added['description'].replace(str(tags), '')

				added['hashtags'] = tag_list
				added['has_hashtags'] = (len(tag_list) > 0)

				char_limit = 450
				tempdesc = added['description'].split('\n\n')
				has_link = [True if re.search(hlink_regex, x) else False for x in tempdesc]
				paragraph_lengths = [len(x) for x in tempdesc]
				total_length = 0

				# Get lengths with links to include by default
				for index in range(0, len(paragraph_lengths)):
					total_length = total_length + (paragraph_lengths[index] if has_link[index] else 0)

				# Repeat process to include non-linked paragraphs
				# Break if beyond character limit
				for index in range(0, len(tempdesc)):
					if not has_link[index]:
						if ((total_length + paragraph_lengths[index]) <= char_limit) or index < 1:
							has_link[index] = True
							if index < 1 and ((total_length + paragraph_lengths[index]) > 2*char_limit):
								paragraph_lengths[index] = char_limit-total_length
								tempdesc[index] = tempdesc[index][0:paragraph_lengths[index]]+"..."
								break

							total_length = total_length + paragraph_lengths[index]						
						else:
							break

				new_desc = []

				for index in range(0, len(tempdesc)):
					if has_link[index]:
						new_desc.append(tempdesc[index])

				added['description'] = '\n\n'.join(str(x) for x in new_desc)

				if 'description' in added:
					hlinkdata = re.findall( hlink_regex, added['description'])
					for link in hlinkdata:
						added['description'] = added['description'].replace(link[0], '<a class="d-inline-flex" target="_blank" href="{}{}">{}</a>'.format("" if link[1] else "http://", link[0], link[0] ))
				fb_content.append(added)

		carousel = render_to_string('main/partials/fb_updates.html', {'fb_data': fb_content}).strip()

		return JsonResponse({'updates': carousel})