import requests

# This file is useful for share the same session token ID (passed by the server when the user log in)
# with others packages. This because SAURUSS has to talk with SAURUSS server several times when
# an alarm occur.

s = requests.Session()
URI = "" #url to the web served removed for security purposes


def doLogin(username, password):
    return s.post(URI + f'login/{username}/{password}/').status_code

def doLogout():
    return s.get(URI + f'logout/').status_code

def getDistances():
    return s.get(URI + 'distances/').text


def sendAlarmBySensorID(sensor_id):
    s.post(URI + f"alarms/{sensor_id}/")


def uploadMediaFile(sensor_id, today, proof):
    s.post(URI + f"upload/{sensor_id}/{today}/", files={"media": proof})


def getTimestampsOfAlarms(sensor_id):
    return s.get(URI + f"alarms/timestamp/{sensor_id}/").text
