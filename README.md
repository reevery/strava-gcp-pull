# Strava to Google Cloud Platform

This repository contains Python code suitable to be pushed to a Google Cloud
Platform Cloud Function.

It is expected to be triggered by a Pub/Sub event which will provide it with
the activity id it should download.

The function will then authenticate against the Strava API, using tokens stored in Secret Manager,
before retrieving the activity and the activity streams and saving them to Cloud Storage.

##Initialisation
### Environment Variables

This Cloud Function requires the following environment variables:

| Environment Variable Name|Explanation|
|---|---|
| GOOGLE_APPLICATION_CREDENTIALS|A path to a JSON credentials file. Within GCP this is set automatically.|
| GCP_PROJECT | The Project Id in which specifically the Secret Manager secrets are stored. Within GCP this is set automatically.|
| STORAGE_BUCKET_NAME| The name (not path) of the Cloud Storage bucket to where the function should save each activity.|

### Authentication
Go into GCP Security > Secret Manager, and add a new version of your Client Id and Client Secret, as found at 
https://www.strava.com/settings/api

With these and your environment variables set, run the authenticate.py script.
This will ask you to navigate to a URL, where you should authenticate, and obtain
a code which needs entering back into the script where it will be exchanged for the access/refresh token pair and saved
to Secret Manager.

## Loading historical activities
You may decide to back-fill your Storage Bucket with historical activities.
A script is provided in fetch_all.py which is intended to download activities not already saved to Cloud Storage.
Please remember that the Strava API is rate-limited, so you may need to run this a few times to get a complete history.
