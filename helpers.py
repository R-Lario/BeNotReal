from flask import Flask, render_template, redirect, session
from functools import wraps
import requests
import json
from geopy.geocoders import Nominatim


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("auth_token") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# BEREAL API's
urls = {
    "login": {
        "sms_req": "https://auth.bereal.team/api/vonage/request-code",
        "sms_submit": "https://auth.bereal.team/api/vonage/check-code",
        "auth_token": "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key=AIzaSyDwjfEeparokD7sXPVQli9NsTuhT6fJ6iA",
        "refresh_token": "https://securetoken.googleapis.com/v1/token?key=AIzaSyDwjfEeparokD7sXPVQli9NsTuhT6fJ6iA"
    },
    "bereal-requests": {
        "friends": "https://mobile.bereal.com/api/feeds/friends",
        "discovery": "https://mobile.bereal.com/api/feeds/discovery",
        "comment": "https://us-central1-alexisbarreyat-bereal.cloudfunctions.net/setCommentPost",
        "send_friend_request": "https://mobile.bereal.com/api/relationships/friend-requests"
    }
}

def get_sms_code(phone_number):
    payload = json.dumps({
        "deviceId": "3DABA022-92B8-4499-889E-29B8F99946A7",
        "phoneNumber": f"{phone_number}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "POST", urls["login"]["sms_req"], headers=headers, data=payload)
    # couldn't request sms code
    if response.status_code != 200:
        return [False]
    # could request sms code and returns vonagereqid
    else:
        return [True, response.json()["vonageRequestId"]]


def submit_sms_code(sms_code, vonageRequestId):
    # -----------SUBMIT SMS CODE-------------------
    payload = json.dumps({
        "code": f"{sms_code}",
        "vonageRequestId": f"{vonageRequestId}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", urls["login"]["sms_submit"], headers=headers, data=payload)
    # sms code is invalid
    if response.status_code != 200:
        return [False, "Invalid code"]
    login_token = response.json()["token"]
    uid = response.json()["uid"]

    # -----------GET AUTH TOKEN-------------------
    payload = json.dumps({
        "returnSecureToken": True,
        "token": f"{login_token}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", urls["login"]["auth_token"], headers=headers, data=payload)
    auth_token = response.json()["idToken"]
    refresh_token = response.json()["refreshToken"]
    return [True, auth_token, refresh_token, uid]

def get_refreshed_token(refresh_token):
    url = urls["login"]["refresh_token"]
    payload = json.dumps({
    "refresh_token": f"{refresh_token}",
    "grant_type": "refresh_token"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return [False]
    else:
        response_body = response.json()
        return [True, response_body["access_token"], response_body["refresh_token"]]


def get_friends_feeds(auth_token):
    url = urls["bereal-requests"]["friends"]
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'user-agent': 'BeReal/7242 CFNetwork/1107.1 Darwin/19.0.0',
        'authorization': f'{auth_token}'
    }
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        return [False, "Couldn't get feed from BeReal servers. Try logging in and logging out."]
    return [True, response.json(), "friends"]


def get_discovery_feeds(auth_token):
    url = urls["bereal-requests"]["discovery"]
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'user-agent': 'BeReal/7242 CFNetwork/1107.1 Darwin/19.0.0',
        'authorization': f'{auth_token}'
    }
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        return [False, "Couldn't get feed from BeReal servers. Try logging in and logging out."]
    return [True, response.json()["posts"], "discovery"]


def comment_on_post(userId, comment, auth_token):
    url = urls["bereal-requests"]["comment"]
    payload = json.dumps({
        "data": {
            "text": f"{comment}",
            "userId": f"{userId}"
        }
    })
    headers = {
        'authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.content)
    if response.status_code != 200:
        return False
    return True

def send_friend_request(user_id, auth_token):
    url = urls["bereal-requests"]["send_friend_request"]
    payload = json.dumps({
    "source": "profile",
    "userId": f"{user_id}"
    })
    headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'user-agent': 'BeReal/7242 CFNetwork/1107.1 Darwin/19.0.0',
    'accept-language': 'en-us',
    'authorization': f'{auth_token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 201:
        return False
    return True


# END BEREAL API's


def get_location(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(
        str(latitude) + "," + str(longitude), language='en')
    address = location.raw['address']
    if address.get('country'):
        country = address.get('country')
    else:
        return "Couldn't determine address"

    if address.get("city"):
        place = address.get("city") + ", " + country
    elif address.get("town"):
        place = address.get("town") + ", " + country
    else:
        place = country
    return place
