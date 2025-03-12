import http.client
import json
import os

DEFAULT_PARAMETERS = {
    "decoding_method": "sample",
    "max_new_tokens": 1000,
    "min_new_tokens": 10,
    "temperature": 0.7
}
DEFAULT_URL = "https://us-south.ml.cloud.ibm.com"


def get_token() -> str:
    ibm_cloud__iam_url = "iam.cloud.ibm.com"

    IBM_KEY = os.getenv("IBM_API_KEY")

    conn_ibm_cloud_iam = http.client.HTTPSConnection(ibm_cloud__iam_url)
    payload = "grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey=" + IBM_KEY
    headers = { 'Content-Type': "application/x-www-form-urlencoded" }
    conn_ibm_cloud_iam.request("POST", "/identity/token", payload, headers)
    res = conn_ibm_cloud_iam.getresponse()
    data = res.read()
    decoded_json = json.loads(data.decode("utf-8"))
    return decoded_json["access_token"]
