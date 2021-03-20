import logging
import json
import os
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


class SecretManager:
    def __init__(self):
        self.client = secretmanager.SecretManagerServiceClient()
        self._client_id = None
        self._client_secret = None
        self._refresh_token = None
        self._access_token = None
        self._expires_at = None

    def _get_secret(self, name):
        _name = f"projects/{os.getenv('GCP_PROJECT')}/secrets/{name}/" \
                f"versions/latest"
        return self.client.access_secret_version(request={
            'name': _name
        }).payload.data.decode('utf-8')

    @property
    def client_id(self):
        if not self._client_id:
            self._client_id = self._get_secret('STRAVA_CLIENT_ID')
        return self._client_id

    @property
    def client_secret(self):
        if not self._client_secret:
            self._client_secret = self._get_secret('STRAVA_CLIENT_SECRET')
        return self._client_secret

    def _get_auth_dict(self):
        auth_secret = self._get_secret('STRAVA_ACCESS_TOKEN')
        logger.debug(auth_secret)
        auth_dict = json.loads(auth_secret)
        self._access_token = auth_dict['access_token']
        self._refresh_token = auth_dict['refresh_token']
        self._expires_at = auth_dict['expires_at']

    @property
    def refresh_token(self):
        if not self._refresh_token:
            self._get_auth_dict()
        return self._refresh_token

    @property
    def access_token(self):
        if not self._access_token:
            self._get_auth_dict()
        return self._access_token

    @property
    def expires_at(self):
        if not self._expires_at:
            self._get_auth_dict()
        return self._expires_at

    def set_auth_dict(self, value: dict):
        self._access_token = value['access_token']
        self._refresh_token = value['refresh_token']
        self._expires_at = value['expires_at']

        parent = self.client.secret_path(os.getenv('GCP_PROJECT'), 'STRAVA_ACCESS_TOKEN')
        self.client.add_secret_version(request={
            "parent": parent,
            "payload": {"data": json.dumps(value).encode('utf-8')}
        })
