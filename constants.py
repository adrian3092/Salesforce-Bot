import json
import os
from google.oauth2 import service_account
from google.cloud import secretmanager
import google.cloud.logging


# set constants
PROJECT_ID = "salesforce-bot-XXXXXX"
JSON_FILE = "service_account.json"
SECRET_NAMES = ("slack_token", "salesforce_authentication", "flask_authentication")
TOKENS = {}


# retrieve tokens from google cloud secret manager
def get_tokens_from_secret_manager(project, json_file, secret_names):
    """
    retrieves tokens from google cloud secret manager
    """
    # check if json file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found...")
        return None

    try:
        with open(json_file) as source:
            info = json.load(source)
        credentials = service_account.Credentials.from_service_account_info(info)
        client = secretmanager.SecretManagerServiceClient(credentials=credentials)
        test_client = google.cloud.logging.Client(credentials=credentials)
        # iterate through secret names in secret manager
        for secret_name in secret_names:
            name = f"projects/{project}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(name=name)
            TOKENS[secret_name] = response.payload.data.decode("UTF-8")
        return (TOKENS, test_client)
    except Exception as error:
        print(f"Error: {error}")
        return None


tokens = get_tokens_from_secret_manager(PROJECT_ID, JSON_FILE, SECRET_NAMES)[0]
logging = get_tokens_from_secret_manager(PROJECT_ID, JSON_FILE, SECRET_NAMES)[1]


# set authentication variables for slack, salesforce and flask
if tokens:
    slack_token = tokens.get("slack_token")
    salesforce_credentials = tokens.get("salesforce_authentication").split("\n")
    flask_credentials = tokens.get("flask_authentication").split("\n")
