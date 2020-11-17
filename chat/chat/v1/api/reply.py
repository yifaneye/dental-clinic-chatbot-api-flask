from abc import abstractmethod
from datetime import date

from http import HTTPStatus
import requests

DENTIST_API_BASE_PATH = 'http://0.0.0.0:8083/v1'
TIMESLOT_API_BASE_PATH = 'http://0.0.0.0:8084/v1'


def list_to_string(_list):
    return f"{', '.join(map(str, _list))}"


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
        self.url = f'{DENTIST_API_BASE_PATH}/dentists'

    def process_api_json_response(self):
        jsonResponse = self.get_api_json_response()
        dentists = [dentist['name'] for dentist in jsonResponse]
        dentistsString = list_to_string(dentists)
        return f'We have {dentistsString}.'


class DentistInformationReply(Reply):
    """A reply to user's request on information about a specific dentist"""

    entityName = __qualname__

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.url = f'{DENTIST_API_BASE_PATH}/dentists?name={name}'

    def process_api_json_response(self):
        jsonResponse = self.get_api_json_response()
        if len(jsonResponse) == 0:
            return f'We do not have dentist {self.name}.'
        dentist = jsonResponse[0]
        return f'Dentist {dentist["name"]} works in {dentist["location"]} and specializes in {dentist["specialization"]}.'


class DentistAvailableTimeslotReply(Reply):
    """A reply to user's request on the available timeslot about a specific dentist"""

    entityName = __qualname__

    def __init__(self, name):
        super().__init__()
        self.name = name
        today = date.today().strftime("%Y-%m-%d")
        self.url = f'{TIMESLOT_API_BASE_PATH}/timeslots?dentist={name}&date={today}&status=available'

    def process_api_json_response(self):
        jsonResponse = self.get_api_json_response()
        if len(jsonResponse) == 0:
            return f'We do not have dentist {self.name}.'
        timeslots = [timeslot['startTime'] for timeslot in jsonResponse]
        timeslotsString = list_to_string(timeslots)
        return f'Dentist {self.name} is available today for 1-hour timeslots those start on {timeslotsString} o\'clock.'


class UpdateTimeslotReply(Reply):
    """A reply to user's request on updating a timeslot"""

    entityName = __qualname__

    def __init__(self, name, action, startTime):
        super().__init__()
        self.name = name
        self.action = action
        self.startTime = startTime
        today = date.today().strftime("%Y-%m-%d")
        self.url = f'{TIMESLOT_API_BASE_PATH}/timeslots?dentist={name}&date={today}&startTime={startTime}'
        self.urlBackup = f'{TIMESLOT_API_BASE_PATH}/timeslots?dentist={name}&date={today}'

    @staticmethod
    def get_api_json_response_alternative(url):
        """Returns the JSON response by making an API call"""
        response = requests.get(url)
        return response.json()

    @staticmethod
    def patch_api_json_response_alternative(url, data):
        """Returns the JSON response by making an API call"""
        response = requests.patch(url, data=data)
        if response.status_code != 200:
            return 'failed to'
        return 'succeed to'

    def process_api_json_response(self):
        jsonResponse = self.get_api_json_response()
        if len(jsonResponse) == 0:
            jsonResponseBackup = self.get_api_json_response_alternative(self.urlBackup)
            standardReply = f'We do not have dentist {self.name} working at {self.startTime} today.'
            if self.action == 'reserve' and len(jsonResponseBackup) >= 1:
                timeSlotBackup = jsonResponseBackup[0]
                return f'{standardReply} I suggest with Dentist {self.name}\'s 1-hour timeslot that start on {timeSlotBackup["startTime"]} o\'clock today.'
            return standardReply
        timeslot = jsonResponse[0]
        url = f'{TIMESLOT_API_BASE_PATH}/{timeslot["id"]}'
        if self.action == 'cancel':
            timeslot['status'] = 'available'
            response = self.patch_api_json_response_alternative(url, data=timeslot)
            return f'I {response} cancel the reservation with dentist {self.name} at {self.startTime} for you.'
        elif self.action == 'reserve':
            timeslot['status'] = 'reserved'
            response = self.patch_api_json_response_alternative(url, data=timeslot)
            return f'I {response} reserve the reservation with dentist {self.name} at {self.startTime} for you.'
