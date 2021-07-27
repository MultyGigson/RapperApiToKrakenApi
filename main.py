from flask import Flask, request, jsonify
import time
import os
import requests
import time
import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
# Read Kraken API key and secret stored in environment variables
api_url = "https://api.kraken.com"
api_key = os.environ['API_KEY_KRAKEN']
api_sec = os.environ['API_SEC_KRAKEN']

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    meassge = "<h1>API</h1>" \
              "<h2>Get Status Recent Deposits.</h2>" \
              "<p>Retrieve information about recent deposits made.</p>" \
              "<h3>Urlpath/DepositStatus?asset=Value&Time=Value</h3>"\
              "<p>Time: Nonce used in construction of API-Sign header.(Type int32 )</p>"\
              "<p>Asset: Asset being deposited.(Type string )</p>"\
              "<h2>Get Ledgers Info </h2>"\
              "<p>Retrieve information about ledger entries. 50 results are returned at a time, the most recent by default.<p>"\
              "<h3>/urlpath/GetLedgersInfo?Time=Value</h3>"\
              "<p>Time: Nonce used in construction of API-Sign header.(Type int32 )</p>"\
              "<h2>Get Deposit Addresses </h2>"\
              "<p>Retrieve (or generate a new) deposit addresses for a particular asset and method.<p>"\
              "<h3>/GetDepositAddresses?asset=value&Time=value&TypeCoin=value</h3>"\
              "<p>Time: Nonce used in construction of API-Sign header.(Type int32 )</p>"\
              "<p>Asset: Asset being deposited.(Type string )</p>"\
              "<p>TypeCoin: Name of the deposit coin type.(Type string )</p>"

    return meassge


# allow both GET and POST requests
@app.route('/DepositStatus', methods=['Get'])
def DepositStatus():
    if 'asset' in request.args and 'Time' in request.args:
        asset = request.args['asset']
        Time = request.args['Time']
        resp = kraken_request('/0/private/DepositStatus',{"nonce": str(Time),"asset": str(asset)})
        return resp.json()

    else:
        return "Error: No id field provided. Please specify an id."



@app.route('GetLedgersInfo', methods=['Get'])
def GetLedgersInfo():
    if 'Time' in request.args:
        Time = request.args['Time']
        resp = kraken_request('/0/private/Ledgers',{"nonce": str(Time)})
        return resp.json()
    else:
        return "Error: No id field provided. Please specify an id."


@app.route('/GetDepositAddresses', methods=['Get'])
def GetDepositAddresses():
    if 'asset' in request.args and 'Time' in request.args and "TypeCoin" in request.args:
        asset = request.args['asset']
        Time = request.args['Time']
        TypeCoin= request.args['TypeCoin']
        resp = kraken_request('/0/private/DepositAddresses',{"nonce": str(Time),"asset": str(asset),"method": TypeCoin})
        return resp.json()
    else:
        return "Error: No id field provided. Please specify an id."


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


if __name__ == '__main__':
    app.run()

