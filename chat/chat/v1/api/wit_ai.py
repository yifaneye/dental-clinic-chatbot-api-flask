from http import HTTPStatus
import requests

from .reply import *
from .secrets import *

DEFAULT_REPLY = "Sorry, I understand your intent but I am not programmed to respond to this intent."
ERROR_REPLY = "Sorry, I can not understand your intent from my training."


def get_reply(message):
    """Return the reply of a given message after processing."""
    url = f'https://api.wit.ai/message?v={WIT_DATETIME}&q={message}'
    headers = {'Authorization': WIT_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code != HTTPStatus.OK:
        raise response.raise_for_status()
    jsonResponse = response.json()
    try:
        if jsonResponse['intents'][0]['name'] == "getDentists":
            return DentistsReply().get_reply()

        elif jsonResponse['intents'][0]['name'] == "getDentistInformation":
            name = jsonResponse['entities']['dentist:dentist'][0]['body']
            return DentistInformationReply(name).get_reply()
        elif jsonResponse['intents'][0]['name'] == "getDentistAvailableTimeslots":
            name = jsonResponse['entities']['dentist:dentist'][0]['body']
            return DentistAvailableTimeslotReply(name).get_reply()
        elif jsonResponse['intents'][0]['name'] == "updateTimeslot":
            name = jsonResponse['entities']['dentist:dentist'][0]['body'] or ''
            action = jsonResponse['entities']['action:action'][0]['body'] or ''
            # Get hour 13 -> 13, 09 -> 9
            startTime = jsonResponse['entities']['wit$datetime:datetime'][0]['value'][11:13].lstrip('0') or ''
            return UpdateTimeslotReply(name, action, startTime).get_reply()
        return DEFAULT_REPLY
    except:
        return ERROR_REPLY
