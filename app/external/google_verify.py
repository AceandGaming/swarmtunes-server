import logging
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from core.paths import SECRETS

log = logging.getLogger()

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.readonly",
]

TOKEN_PATH = SECRETS / "token.json"
CREDENTIALS_PATH = SECRETS / "credentials.json"


def get_google_credentials():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES
        )

        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message="Please visit this URL: {url}",
            success_message="The auth flow is complete; you can close this tab.",
            open_browser=True,
            prompt="consent",
            access_type="offline",
        )

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    log.info("Google credentials verified and saved!")
    return creds
