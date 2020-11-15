from http import HTTPStatus
import requests

from .reply import *
from .secrets import *

DEFAULT_REPLY = "Sorry, I don't understand"


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
	except:
		return DEFAULT_REPLY
