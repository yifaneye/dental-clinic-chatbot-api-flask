from abc import abstractmethod

from http import HTTPStatus
import requests


class Reply:
    """A reply to user's request"""

    entityName = __qualname__

    def __init__(self):
        """Initializes the reply"""
        self.url = ''
        self.headers = {}

    def get_api_json_response(self):
        """Returns the JSON response by making an API call"""
        response = requests.get(self.url, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            raise response.raise_for_status()
        return response.json()

    @abstractmethod
    def process_api_json_response(self):
        """Returns the reply processed from JSON response"""
        raise NotImplementedError

    @classmethod
    def get_default_reply(cls):
        """Returns the default reply"""
        return f'{cls.entityName} data processing error'

    def get_reply(self):
        """Returns the reply to the given parameter(s)"""
        try:
            return self.process_api_json_response()
        except:
            return self.get_default_reply()


class DentistsReply(Reply):
    """A reply to user's request on all available dentists"""

    entityName = __qualname__

    def __init__(self):
        super().__init__()
        self.url = f'http://0.0.0.0:8082/api/dentist/'

    def process_api_json_response(self):
        jsonResponse = self.get_api_json_response()
        dentists = [dentist['name'] for dentist in jsonResponse]
        dentistsString = '%s' % ', '.join(map(str, dentists))
        return f'We have {dentistsString}.'
