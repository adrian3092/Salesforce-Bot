# Salesforce Bot

This application retrieves a list of customers from a custom report in Salesforce, stores the customer names in a list and exposes that list in JSON format using Flask.

> [!NOTE]
> The endpoint to retrieve the list of customers is authenticated. Any sensitive information such as tokens, usernames and passwords are stored in Google Cloud Secret Manager.

I chose to use Python Client for Cloud Logging to centralize all logs within Google Cloud so that they can be accessed via Logs Explorer.
