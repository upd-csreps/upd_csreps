from django.conf import settings
from django.shortcuts import render, redirect
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import secrets

# Create your views here.

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

		required_fields = ['alias', 'concerns-details', 'email', 'phone']
		required_complete = True

		for field in required_fields:
			if not (data.get(field, None)):
				required_complete = False
				break

		if required_complete:
			sheetdata_range = 'Data!A2:K'
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
