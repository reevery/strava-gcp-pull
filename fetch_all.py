""" Retrieve historic activities from Strava

The code in main.py only pulls one activity at a time. If you would like to
download a history of your activities, then execute this script.

Please note that the Strava API is rate limited, so you may need to execute
this a few times. It will check for existing files in your Storage Bucket
before attempting to download a file.
"""
import logging
from main import *

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    # Check if a fresh token is required.
    if sm.expires_at < datetime.now().timestamp():
        refresh_access_token()
    client = Client(access_token=sm.access_token)

    # Initialise Google Cloud Storage.
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.getenv('STORAGE_BUCKET_NAME'))
    bucket_names = [os.path.splitext(b.name)[0] for b in bucket.list_blobs()]
    logger.debug(bucket_names)

    # Download a list of activities.
    activities = client.get_activities()
    logger.info('There are %s activities', len(list(activities)))

    # Download each activity, if its name (Id) is not in your Storage Bucket.
    for activity in [a for a in activities if a.name not in bucket_names]:
        get_activity({'data': base64.b64encode(
            json.dumps({'object_id': activity.id}).encode('utf-8'))})
