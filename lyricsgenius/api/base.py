import time
from functools import wraps

import requests
from requests.exceptions import HTTPError, Timeout

from lyricsgenius.exceptions import TokenRequiredError


class Sender(object):
    """Sends requests to Genius."""
    # Create a persistent requests connection
    _SLEEP_MIN = 0.2  # Enforce minimum wait time between API calls (seconds)
    API_ROOT = 'https://api.genius.com/'
    PUBLIC_API_ROOT = 'https://genius.com/api/'

    def __init__(
        self,
        access_token=None,
        response_format='plain',
        timeout=5,
        sleep_time=0.5
    ):
        self._session = requests.Session()
        self._session.headers = {
            'application': 'LyricsGenius',
            'User-Agent': 'https://github.com/johnwmillr/LyricsGenius'
        }
        self.access_token = access_token
        if access_token is not None:
            self._session.headers['authorization'] = 'Bearer ' + self.access_token
        self.response_format = response_format.lower()
        self.timeout = timeout
        self.sleep_time = sleep_time

    def _make_request(
        self,
        path,
        method='GET',
        params_=None,
        public_api=False,
        **kwargs
    ):
        """Makes a request to the API."""
        if public_api:
            uri = self.PUBLIC_API_ROOT
            header = self._session.headers.pop('authorization', None)
        else:
            uri = self.API_ROOT
            header = None
        uri += path

        params_ = params_ if params_ else {}

        # Make the request
        response = None
        try:
            response = self._session.request(method, uri,
                                             timeout=self.timeout,
                                             params=params_,
                                             **kwargs)
            response.raise_for_status()
        except Timeout as e:
            error = "Request timed out:\n{e}".format(e=e)
            raise Timeout(error)
        except HTTPError as e:
            error = str(e)
            res = e.response.json()
            description = (res['meta']['message']
                           if res.get('meta')
                           else res.get('error_description'))
            error += '\n{}'.format(description) if description else ''
            raise HTTPError(response.status_code, error)

        if header:
            self._session.headers['authorization'] = header

        # Enforce rate limiting
        time.sleep(max(self._SLEEP_MIN, self.sleep_time))

        if response.status_code == 200:
            res = response.json()
            return res['response'] if "response" in res else res
        elif response.status_code == 204:
            return 204
        else:
            raise AssertionError('Response status code was neither 200, nor 204!')


public_api_msg = (
    "Using this method with the developers API needs an access token."
    " Get an access token or"
    " use the public API by setting"
    " public_api=True in method parameters."
)

def check_token(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.access_token is None:
            public_method = "public_api" in func.__code__.co_varnames
            if public_method:
                if kwargs.get("public_api", False) is False:
                    msg = public_api_msg
                    raise TokenRequiredError(msg)
            else:
                raise TokenRequiredError()
        return func(self, *args, **kwargs)
    return wrapper
