import os
import logging
import socket
from flask import Flask, jsonify, send_from_directory
from flask_httpauth import HTTPBasicAuth
import requests
import constants


app = Flask(__name__)
auth = HTTPBasicAuth()


# initialize logging client
client = constants.logging
client.setup_logging()


# create empty list to store customers
sfdc_customer_list = []


# this is defining a route for the status page
@app.route("/status")
def home():
    """
    status page, returns OK if working
    """
    return ("<h1>OK</h1>"), 200


# this is defining a route for the favicon.ico file
@app.route("/favicon.ico")
def favicon():
    """
    this function returns the favicon file from the specified directory
    """
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


# query customers from salesforce
def customers_list():
    """
    get list of customers from salesforce
    """
    # define the necessary parameters for the api request
    parameters = {
        "grant_type": "password",
        "client_id": constants.salesforce_credentials[0],
        "client_secret": constants.salesforce_credentials[1],
        "username": constants.salesforce_credentials[2],
        "password": constants.salesforce_credentials[3],
    }
    # create an empty dictionary to store the data
    data = {}
    # clear sfdc_customer_list
    sfdc_customer_list.clear()
    # send a post request to obtain the access token
    logging.info(
        {
            "Host": socket.gethostname(),
            "Message": "Salesforce Bot is requesting a token from Salesforce.",
        }
    )
    get_token = requests.post(
        url="https://login.salesforce.com/services/oauth2/token",
        params=parameters,
        timeout=60
    )
    # extract the access token from the response
    sf_token = get_token.json().get("access_token")
    # define the header for the api request
    sf_header = {
        "Content-type": "application/json",
        "Authorization": "Bearer %s" % sf_token,
    }
    # send a get request to retrieve the list of customers
    logging.info(
        {
            "Host": socket.gethostname(),
            "Message": "Salesforce Bot is requesting customer list from Salesforce.",
        }
    )
    raw_data = requests.get(
        url="https://company.my.salesforce.com/services/data/v51.0/analytics/reports/0000x0000000XxXXXX",
        headers=sf_header,
        json=data,
        timeout=60
    )
    # extract the customers data from the response and store in list
    for customer in raw_data.json()["factMap"]["T!T"]["rows"]:
        sfdc_customer_list.append(customer["dataCells"][0]["label"])
    return "", 200


# authentication for customers endpoint
flask_users = {
    constants.flask_credentials[0]: constants.flask_credentials[1],
}


@auth.verify_password
def verify_password(username, password):
    """
    verify credentials
    """
    if username in flask_users and flask_users[username] == password:
        return username
    return None


# define a route to return list of customers as json
@app.route("/customers", methods=["GET"])
@auth.login_required
def customers():
    """
    call function to retrieve list of customers from salesforce
    and return results in json format
    """
    customers_list()
    # create an empty list to store the results
    results = []
    # loop through each item in list
    for customer in sfdc_customer_list:
        results.append({"name": customer})
    # return the results as a json response
    logging.info(
        {
            "Host": socket.gethostname(),
            "Message": "Infra Bot is sending customer list to Jira.",
        }
    )
    return jsonify(results), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
