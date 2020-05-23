"""
Helper function to authenticate against Strava API
"""
import logging
from stravalib import Client
from secretmanager import SecretManager
from google.api_core.exceptions import PermissionDenied
import json

logger = logging.getLogger(__name__)

sm = SecretManager()


def authenticate():
    client = Client()
    url = client.authorization_url(client_id=sm.client_id,
                                   redirect_uri='http://localhost')
    logger.info('Open this URL, then paste in the code provided in the URL: '
                '%s', url)
    code = input('Paste code here: ')

    auth_dict = client.exchange_code_for_token(
        client_id=sm.client_id,
        client_secret=sm.client_secret,
        code=code)
    logger.debug('Auth Dict: %s', auth_dict)

    # Save the dict back to Secret manager
    try:
        sm.set_auth_dict(auth_dict)
    except PermissionDenied:
        logger.error(f'Looks like your token could not be saved. Try manually '
                     f'adding this value to your STRAVA_ACCESS_TOKEN secret:\n'
                     f'  {json.dumps(auth_dict)}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    authenticate()
