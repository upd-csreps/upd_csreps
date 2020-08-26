from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from googleapiclient.discovery import build
from google.oauth2 import service_account
import secrets

def sheet_query(page_ct=1, ql_command='select *',qtype=1):
	results = None
	page_ct = page_ct-1

	for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
		try:
			if(settings.DEBUG):
				print("Connecting to Google Sheets..")
			creds = service_account.Credentials.from_service_account_info(settings.TSHOOT_CREDS, scopes=settings.GOOGLE_API_SCOPES)
			service = build('sheets', 'v4', credentials=creds)
			sheet = service.spreadsheets()

			service.spreadsheets().values().clear(
				spreadsheetId=settings.TSHOOT_SPREADSHEET, 
				range="Query!A1:L", body={})

			body = {
				'values': [["=QUERY(Data!A2:L, \"{0} order by A desc limit 10 offset {1}\")".format(ql_command, page_ct*10)]]
			}

			to_write = 'Query{0}'.format(qtype if qtype!= 1 else '')
			
			service.spreadsheets().values().update(
			spreadsheetId=settings.TSHOOT_SPREADSHEET, range='{0}!A1:A1'.format(to_write),
			valueInputOption='USER_ENTERED', body=body).execute()

			range_names = ['{0}!A1:L'.format(to_write)]
			result = service.spreadsheets().values().batchGet(
				spreadsheetId=settings.TSHOOT_SPREADSHEET, ranges=range_names).execute()
			results = result.get('valueRanges', [])	
			if len(results) > 0:
				results = results[0].get('values', [])
			break
		except Exception as e:
			if settings.DEBUG: print(e)
			results = -1

	return results 

def admin(request):
	if request.method == 'GET':
		context = {}
		return render(request, 'troubleshooter/admin.html', context)
	elif request.method == 'POST':
		action = request.GET.get('act', None)
		ql_command = None
		qtype = 1

		if action == "concerns":
			ql_command = "select * where L = ''"
		elif action == "answers":
			ql_command = "select * where L != ''"
			qtype = 2

		if ql_command:
			concerns = sheet_query(ql_command=ql_command, qtype=qtype)
			if type(concerns) != 'int':
				new_concerns = []
				for concern in concerns:
					if concern[0] == '#N/A':
						break

					to_app = {'date':  datetime.strptime(concern[0], '%Y-%m-%d %H:%M:%S'),
						'alias': concern[1],
						'type': concern[2],
						'details': concern[3],
						'attachment': concern[4],
						'email': concern[5],
						'number': concern[6],
						'message': concern[7],
						'consultation': (concern[8] == 'TRUE'),
						'hidden': (concern[9] == 'TRUE'),
						'token' : concern[10],
						'answer': ''
					}

					try:
						to_app['answer'] = concern[11]
					except:
						pass

					new_concerns.append(to_app)

				response = render_to_string('troubleshooter/partials/admin_response.html', {'concerns': new_concerns}).strip()

				return JsonResponse({'response': response})

		return None

		
def index(request):
	concern_type = [
		'General',
		'Academic-Related',
		'Facilities',
		'CS Reps Projects & Services',
		'CS Network',
		'Community'
	]

	if request.method == 'GET':
		context = {'concern_type': concern_type}
		return render(request, 'troubleshooter/index.html', context)
	elif request.method == 'POST':
		data = request.POST
		queries = request.GET

		if queries.get('act', None) == "response":
			concerns = sheet_query(ql_command="select A, B, C, D, L where J != TRUE and L != ''")

			if type(concerns) != 'int':
				new_concerns = []
				for concern in concerns:
					new_concerns.append({'date': datetime.strptime(concern[0], '%Y-%m-%d %H:%M:%S'),
						'alias': concern[1],
						'type': concern[2],
						'details': concern[3],
						'answer': concern[4]
					})
				# context['concerns'] = new_concerns
			return JsonResponse({'response': new_concerns})
		else:
			required_fields = ['alias', 'concerns-details', 'email', 'phone']
			required_complete = True

			for field in required_fields:
				if not (data.get(field, None)):
					required_complete = False
					break

			if required_complete:
				sheetdata_range = 'Data!A2:L'
				for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
					try:
						if(settings.DEBUG):
							print("Connecting to Google Sheets..")
						creds = service_account.Credentials.from_service_account_info(settings.TSHOOT_CREDS, scopes=settings.GOOGLE_API_SCOPES)
						service = build('sheets', 'v4', credentials=creds)
						sheet = service.spreadsheets()

						timestamp = datetime.now()
						token = secrets.token_urlsafe(16)

						body = {
							'values': [
								[ str(timestamp), 
								  data['alias'],
								  concern_type[int(data['concerns'])], 
								  data['concerns-details'],
								  data['attachment'], #Replace this with Google Drive IDs
								  data['email'],
								  data['phone'],
								  data['message'],
								  '='+str(bool(data.get('consultation', False))).upper(),
								  '='+str(bool(data.get('hideResponse', False))).upper(),
								  str(token)
								],
							]
						}

						result = sheet.values().append(spreadsheetId=settings.TSHOOT_SPREADSHEET, 
							range=sheetdata_range, valueInputOption='USER_ENTERED', body=body).execute()
						print(result.get('updates'))
						break
					except Exception as e:
						if settings.DEBUG: print(e)

				return redirect('troubleshooter:index')
			else:
				context = {'concern_type': concern_type}
				return render(request, 'troubleshooter/index.html', context)
