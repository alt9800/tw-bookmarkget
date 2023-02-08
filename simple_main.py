import base64
import hashlib
import os
import re
import json
import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session

# 注意書きを削った動作検証用
client_id = os.environ.get("CLIENT_ID")

redirect_uri = "https://www.example.com"

scopes = ["bookmark.read", "tweet.read", "users.read", "offline.access" ]

code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
print(oauth)

auth_url = "https://twitter.com/i/oauth2/authorize"
authorization_url, state = oauth.authorization_url(
    auth_url, code_challenge=code_challenge, code_challenge_method="S256"
)

print(
    "Visit the following URL to authorize your App on behalf of your Twitter handle in a browser:"
)
print(authorization_url)

authorization_response = input(
    "Paste in the full URL after you've authorized your App:\n"
)


token_url = "https://api.twitter.com/2/oauth2/token"

auth = False


token = oauth.fetch_token(
    token_url=token_url,
    authorization_response=authorization_response,
    auth=auth,
    client_id=client_id,
    include_client_id=True,
    code_verifier=code_verifier,
)


access = token["access_token"]

user_me = requests.request(
    "GET",
    "https://api.twitter.com/2/users/me",
    headers={"Authorization": "Bearer {}".format(access)},
).json()
user_id = user_me["data"]["id"]

# Make a request to the bookmarks url
url = "https://api.twitter.com/2/users/{}/bookmarks".format(user_id)
headers = {
    "Authorization": "Bearer {}".format(access),
    "User-Agent": "BookmarksSampleCode",
}
response = requests.request("GET", url, headers=headers)
if response.status_code != 200:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )
print("Response code: {}".format(response.status_code))
json_response = response.json()


with open("data.json", "a") as f:
    json.dump(json_response, f , indent=4, sort_keys=True)

print(json.dumps(json_response, indent=4, sort_keys=True))
