from googleapiclient.discovery import build
from google.oauth2 import service_account

scopes = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheet_id = '1CvtndPwxO53BkvbWblIlfvazeu69a3UWGWfU3hVK5rA'
spreadsheet_range = 'Sheet1!A1:F4'

def main():
    print("Connecting to Google Sheets...")
    creds = service_account.Credentials.from_service_account_file('troubleshooter-creds.json', scopes=scopes)
    #creds = service_account.Credentials.from_service_account_info(api_creds, scopes=api_scopes)
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

    

if __name__ == '__main__':
    main()