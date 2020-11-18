import requests
import json
import pandas as pd
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import googleapiclient.discovery
import pickle

engine = sqlalchemy.create_engine(
    'mssql+pyodbc://sa:Carito33156@VDEV003/Qualex_Stage_SM?driver=ODBC+Driver+17+for+SQL+Server')


API_KEY = "AIzaSyCu9sZyAu11ZKOeAxAgOBEF--ZRYeMFRJg"


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
                                                                 scopes=["https://www.googleapis.com/auth/youtube.readonly"])

                flow.run_local_server(
                    port=8080, prompt="consent", authorization_prompt_message='')
                self.credentials = flow.credentials

                with open("token.pickle", "wb") as f:
                    print("Saving Credentials for future use...")
                    pickle.dump(self.credentials, f)
                    # print(self.credentials.to_json())

    def get_channel_stats(self):
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        # print(url)
        response = requests.get(url)
        data = json.loads(response.text)
        # print(data)
        try:
            data = data["items"][0]["statistics"]
        except:
            data = None
        self.channel_statistics = data
        return data

    def get_channel_video_data(self):
        channel_videos = self._get_channel_videos(limit=50)
        # print(channel_videos)

        parts = ["snippet", "statistics", "contentDetails"]
        for video_id in channel_videos:
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)
        self.video_data = channel_videos
        return channel_videos

    def _get_single_video_data(self, video_id, part):
        url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0][part]
        except:
            print("error")
            data = dict()
        return data

    def _get_channel_videos(self, limit=None):
        url = f"https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=id&order=date"
        if limit is not None and isinstance(limit, int):
            url += "&maxResults=" + str(limit)
        # print(url)

        vid, npt = self._get_channel_videos_per_page(url)
        idx = 0
        while (npt is not None and idx < 10):
            nexturl = url + "&pageToken=" + npt
            next_vid, npt = self._get_channel_videos_per_page(nexturl)
            vid.update(next_vid)
            idx += 1

        return vid

    def _get_channel_videos_per_page(self, url):
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = dict()
        if 'items' not in data:
            return channel_videos, None
        item_data = data['items']
        nextPageToken = data.get("nextPageToken", None)

        for item in item_data:
            try:
                kind = item['id']['kind']
                if kind == 'youtube#video':
                    video_id = item['id']['videoId']
                    channel_videos[video_id] = dict()
            except KeyError:
                print("error")
        return channel_videos, nextPageToken

    def dump(self):
        if self.channel_statistics is None or self.video_data is None:
            print('No Data found')
            return

        fused_data = {"video_data": self.video_data}
        channel_title = self.video_data.popitem()[1].get(
            'channelTitle', self.channel_id)
        channel_title = channel_title.replace(" ", "_")
        file_name = channel_title+'.json'
        with open(file_name, 'w') as f:
            json.dump(fused_data, f, indent=4)

    def get_channel_subscriber_list(self):

        channel_subscribers = self._get_channel_subscribers()
        # print(channel_videos)

        for subscriber_id in channel_subscribers:

            data = self._get_single_subscriber_data(subscriber_id)
            channel_subscribers[subscriber_id].update(data)
        self.subscriber_data = channel_subscribers

        fused_data = {"subscribers_data": self.subscriber_data}
        channel_id = self.channel_id

        file_name = channel_id+'.json'
        with open(file_name, 'w') as f:
            json.dump(fused_data, f, indent=4)

        return channel_subscribers

    def _get_channel_subscribers(self):
        if self.maxResults is not None and isinstance(self.maxResults, int):
            maxResults = self.maxResults

        youtube = googleapiclient.discovery.build(
            self.api_service_name,
            self.api_version,
            credentials=self.credentials)
        request = youtube.subscriptions().list(
            part="snippet",
            mySubscribers=True,
            maxResults=self.maxResults
        )
        response = request.execute()

        nextPageToken = response.get("nextPageToken", None)
        # print(nextPageToken)
        sub, npt = self._get_channel_subscribers_per_page(nextPageToken)
        # print(npt)
        idx = 0
        while (npt is not None and idx < 10):
            nextPage = npt
            next_sub, npt = self._get_channel_subscribers_per_page(nextPage)

            sub.update(next_sub)
            idx += 1

        return sub

    def _get_channel_subscribers_per_page(self, npt):
        youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=self.credentials)
        request = youtube.subscriptions().list(
            part="snippet",
            mySubscribers=True,
            maxResults=self.maxResults,
            pageToken=npt
        )
        response = request.execute()
        subscribers = dict()
        if 'items' not in response:
            return subscribers, None
        item_data = response['items']

        nextPageToken = response.get("nextPageToken", None)

        for item in item_data:
            try:
                subscirber_id = item['snippet']['channelId']

                subscribers[subscirber_id] = dict()
            except KeyError:
                print("error---")
        return subscribers, nextPageToken

    def _get_single_subscriber_data(self, subscriber_id):
        url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={subscriber_id}&key={self.api_key}'
        # print(url)
        response = requests.get(url)
        data = json.loads(response.text)
        # print(data)
        try:
            data = data["items"][0]["snippet"]
        except:
            data = None
        self.channel_subscribers = data
        return data

    def get_channel_analytics_metrics(self):
        youtube = googleapiclient.discovery.build(
            self.api_analytics_service_name, self.api_analytics_version, credentials=self.credentials)
        request = youtube.reports().query(
            ids="channel=="+self.channel_id,
            startDate='2020-10-01',
            endDate='2020-10-05',
            metrics='annotationClickThroughRate,annotationCloseRate,estimatedMinutesWatched,averageViewDuration,views,shares,likes,dislikes,subscribersGained,subscribersLost,comments',
            dimensions='day',
            sort='day'
        )
        response = request.execute()
        columns = response['columnHeaders']
        rows = response['rows']
        headers = []
        for col in columns:
            header = col['name']
            headers.append(header)
        df = pd.DataFrame(rows, columns=headers)
        print(df)
        #df.to_sql(name='Analytics_Report_Data',schema='QLX-Youtube',con=engine ,if_exists='replace')
        # print(headers)

    def load_data_to_sql(self):
        if self.video_data is not None:
            with open('QualexConsulting.json') as f:
                data = json.load(f)
            stats = data
            video_stats = stats["video_data"]
            sorted_vids = sorted(video_stats.items(), key=lambda item: int(
                item[1]["viewCount"]), reverse=True)
            stats = []
            for vid in sorted_vids:
                video_id = vid[0]
                video_title = vid[1]["title"]
                video_desc = vid[1]["description"]
                total_likes = vid[1]["likeCount"]
                total_dislikes = vid[1]["dislikeCount"]
                total_comments = vid[1]["commentCount"]
                total_views = vid[1]["viewCount"]
                publishedAt = vid[1]["publishedAt"]
                total_favorite = vid[1]["favoriteCount"]
                channel_id = vid[1]["channelId"]
                channel_title = vid[1]["channelTitle"]
                #tags = vid[1]["tags"]
                stats.append([video_id, video_title, video_desc, total_likes, total_dislikes,
                              total_comments, total_views, publishedAt, total_favorite, channel_id, channel_title])

            df = pd.DataFrame(stats, columns=["video_id", "video_title", "video_desc", "total_likes", "total_dislikes",
                                              "total_comments", "total_views", "publishedAt", "total_favorite", "channel_id", "channel_title"])
            df.to_sql(name='Video_Data', schema='QLX-Youtube',
                      con=engine, if_exists='replace')

        if self.channel_subscribers is not None:
            with open(self.channel_id + '.json') as f:
                data = json.load(f)

            stats = data
            subscribers_data = stats["subscribers_data"]
            # print(subscribers_data)
            stats = []
            for sub in subscribers_data:
                # print(subscribers_data[sub]['title'])
                channel_id = self.channel_id
                subscriber_id = sub
                subscriber_title = subscribers_data[sub]['title']
                subscriber_desc = subscribers_data[sub]['description']
                try:
                    customUrl = subscribers_data[sub]['customUrl']
                except KeyError:
                    customUrl = None
                publishedAt = subscribers_data[sub]['publishedAt']

                stats.append([channel_id, subscriber_id, subscriber_title,
                              subscriber_desc, customUrl, publishedAt])

            df = pd.DataFrame(stats, columns=[
                              "channel_id", "subscriber_id", "subscriber_title", "subscriber_desc", "customUrl", "publishedAt"])
            df.to_sql(name='Channel_Subscribers_Data',
                      schema='QLX-Youtube', con=engine, if_exists='replace')


channel_id = "UCHICL3KWlaWHZA4oCn1igIA"
qlx_channel = YTstats(API_KEY, channel_id)
#data = qlx_channel.get_channel_stats()
# print(data)
# qlx_channel.get_channel_stats()
# qlx_channel.get_channel_video_data()

# qlx_channel.dump()
# qlx_channel.get_channel_subscriber_list()
# qlx_channel.load_data_to_sql()
qlx_channel.get_channel_analytics_metrics()
