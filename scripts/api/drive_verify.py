from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from scripts.paths import SECRETS_DIR

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    creds = None
    if os.path.exists(SECRETS_DIR / 'token.json'):
        creds = Credentials.from_authorized_user_file(SECRETS_DIR / 'token.json', SCOPES)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(SECRETS_DIR / 'credentials.json', SCOPES)
        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='The auth flow is complete; you can close this tab.',
            open_browser=True,
            prompt='consent',
            access_type='offline'
        )
        with open(SECRETS_DIR / 'token.json', 'w') as token:
            token.write(creds.to_json())

    return creds