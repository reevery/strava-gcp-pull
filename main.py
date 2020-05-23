import logging
import os
import json
from stravalib import Client
from google.cloud import storage
from secretmanager import SecretManager
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

# These are all of the supported stream types available from Strava's API.
STREAM_TYPES = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
                'heartrate', 'cadence', 'watts', 'temp', 'moving',
                'grade_smooth']

sm = SecretManager()


def refresh_access_token():
    """
    Client posts a valid access token and refresh token and receives a dict
    containing 'access_token', 'refresh_token', and 'expires_at'.
    The function then saves this to Secret Manager
    """
    client = Client(sm.access_token)
    auth_dict = client.refresh_access_token(
        client_id=sm.client_id,
        client_secret=sm.client_secret,
        refresh_token=sm.refresh_token)
    logger.debug('Auth Dict: %s', auth_dict)

    # Save the dict back to Secret Manager
    sm.set_auth_dict(auth_dict)


def get_activity(event: dict, context=None):
    """
    Retrieve the given activity, and its streams, and save the data as one
    json file to Cloud Storage.

    Args:
        event (dict): Dict in Pub/Sub format
        context: Not used
    """
    # Initialise Google Cloud Storage. Doing this first because to save an
    # API call if there is a problem loading the bucket.
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.getenv('STORAGE_BUCKET_NAME'))

    # Parse the Pub/Sub message data.
    data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    logging.info(data)

    # Check if a fresh token is required.
    if sm.expires_at < datetime.now().timestamp():
        refresh_access_token()
    client = Client(access_token=sm.access_token)

    # Check we're logged in correctly.
    logger.info('Logged in as athlete %s', client.get_athlete())

    # Download the activity data.
    activity = client.get_activity(data['object_id'])
    activity_dict = activity.to_dict()
    logger.debug('Activity %s: %s', activity.id, activity_dict)

    # Download the streams data.
    streams = client.get_activity_streams(activity.id, STREAM_TYPES)
    logger.debug(streams)

    # Append the streams data to the activity data. This is the only
    # manipulation in this workflow; everything else should be manipulated
    # when you read this file from Cloud Storage.
    activity_dict['streams'] = {k: v.to_dict() for k, v in streams.items()}
    logger.debug(activity_dict)

    # Save to Cloud Storage.
    blob = bucket.blob(f'{activity.id}.json')
    blob.upload_from_string(json.dumps(activity_dict),
                            content_type="application/json")

    return 0
