from googleapiclient.http import MediaFileUpload
import os
import pickle
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request

class upload_to_GD:

    def Create_Service(self, client_secret_file, api_name, api_version, *scopes):
        print(client_secret_file, api_name, api_version, scopes, sep='-')
        CLIENT_SECRET_FILE = client_secret_file
        API_SERVICE_NAME = api_name
        API_VERSION = api_version
        SCOPES = [scope for scope in scopes[0]]
        print(SCOPES)

        cred = None

        pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
        # print(pickle_file)

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server()

            with open(pickle_file, 'wb') as token:
                pickle.dump(cred, token)

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
            print(API_SERVICE_NAME, 'service created successfully')
            return service
        except Exception as e:
            print('Unable to connect.')
            print(e)
            return None

    ##def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    #    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    #return dt

    def call_upload(self, file_names):
        CLIENT_SECRET_FILE = '../static/JSON/mileto-app-89d40dd3936c.json'
        API_NAME = 'drive'
        API_VERSION = 'v3'
        SCOPES = ['https://www.googleapis.com/auth/drive']

        service = self.Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

        folder_id = '17BskLL0bgyjnsTTsXv6OkuXASzyylej7'

        mime_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/x-spss-sav']

        for file_name, mime_type in zip(file_names, mime_types):
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaFileUpload('../static/models/{0}'.format(file_name), mimetype=mime_type)

            service.files().create(
                body = file_metadata, 
                media_body = media,
                fields = 'id'
            ).execute()