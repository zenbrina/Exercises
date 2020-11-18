import requests
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import googleapiclient.discovery
import pickle


# channel_id="UCE2JDtOSy6R-9dwkGIWgyEA"
channel_id = "UCSZbXT5TLLW_i-5W8FZpFsg"
API_KEY = "AIzaSyBblg7lCEmOY147w2PtRI7wY6z75IjM79Y"


class YTstats:
    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_statistics = None
        self.video_data = None
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.api_analytics_service_name = "youtubeanalytics"
        self.api_analytics_version = "v2"
        self.maxResults = 5
        self.channel_subscribers = None
        self.credentials = None
        if os.path.exists("token.pickle"):
            print("Loading Credentials From File...")
            with open("token.pickle", "rb") as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("Refreshing Access Token...")
                self.credentials.refresh(Request())
            else:
                print("Requesting New Tokens...")

                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json",
                                                                 #scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
                                                                 #scopes = ["https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]
                                                                 #scope = ["https://www.googleapis.com/auth/youtube"]
                                                                 scope=[
                                                                     "https://www.googleapis.com/auth/youtubepartner"]
                                                                 )

                flow.run_local_server(
                    port=8080, prompt="consent", authorization_prompt_message='')

                self.credentials = flow.credentials

                with open("token.pickle", "wb") as f:
                    print("Saving Credentials for future use...")
                    pickle.dump(self.credentials, f)
                    # print(self.credentials.to_json())

    def check_access(self):
        try:

            youtube = googleapiclient.discovery.build(
                self.api_analytics_service_name, self.api_analytics_version, credentials=self.credentials)
            request = youtube.reports().query(
                ids="channel=="+self.channel_id,
                #ids = "channel==MINE",
                #managedByMe = True,
                startDate='2020-10-05',
                endDate='2020-10-05',
                metrics='annotationClickThroughRate,annotationCloseRate,estimatedMinutesWatched,averageViewDuration',
                dimensions='day',
                sort='day'
            )
            response = request.execute()

            print(response)

        except Exception as ex:
            print(ex)


test1 = YTstats(API_KEY, channel_id)
test1.check_access()
