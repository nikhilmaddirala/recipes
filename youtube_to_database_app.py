import json
from helpers.youtube_helpers import get_video_id, get_transcript_text
import os
from googleapiclient.discovery import build
import re
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()

def create_youtube_client():
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    return youtube

def get_channel_id_from_video_id(youtube, video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response['items'][0]['snippet']['channelId']

def get_videos_from_channel(youtube, channel_id):
    videos = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Maximum allowed by the API
            type='video',
            pageToken=next_page_token
        )

        response = request.execute()
        video_ids = [item['id']['videoId'] for item in response['items']]
        
        videos_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids)
        )
        
        videos_response = videos_request.execute()
        videos.extend(videos_response['items'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    videos_flattened = []
    for item in videos:
        flattened_video = {}

        # Flatten 'snippet', 'contentDetails', and 'statistics'
        flattened_video['videoId'] = item['id']
        for key in ['snippet', 'contentDetails', 'statistics']:
            flattened_video.update(item[key])

        videos_flattened.append(flattened_video)
    
    return videos_flattened


class GSpreadsheet:
    def __init__(self, spreadsheet_title):
        self.scope =  [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('.secrets/gsheets_credentials.json', self.scope)
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open(spreadsheet_title)

    def get_worksheet(self, worksheet_title):
        worksheet = self.spreadsheet.worksheet(worksheet_title)
        return GTable(worksheet)

class GTable:
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.headers = self.get_headers()

    def get_headers(self):
        if self.worksheet.row_count > 0:
            return self.worksheet.row_values(1)
        else:
            return []

    def insert_headers_from_data(self, data):
        headers = list(data[0].keys())
        self.headers = headers
        self.worksheet.append_row(headers)       

    def insert_rows_from_data(self, data):
        # Get all existing records from the worksheet
        all_records = self.worksheet.get_all_records()

        # Prepare a list to hold the new rows
        new_rows = []

        # Iterate over each dictionary in the data
        for row in data:
            # Convert all values in the dictionary to JSON strings
            row_as_strings = {
                key: json.dumps(value) if not isinstance(value, str) else value
                for key, value in row.items()
            }

            # Convert the dictionary to a list of values
            row_values = list(row_as_strings.values())

            # If the row does not already exist in the worksheet, add it to the list of new rows
            if row_values not in all_records:
                new_rows.append(row_values)

        # If there are any new rows, append them to the worksheet
        if new_rows:
            self.worksheet.append_rows(new_rows)


def main():
    youtube = create_youtube_client()
    video_url = 'https://www.youtube.com/watch?v=6RjyW2kcgSE'
    video_id = get_video_id(video_url)
    channel_id = get_channel_id_from_video_id(youtube, video_id)
    video_data = get_videos_from_channel(youtube, channel_id)
    spreadsheet = GSpreadsheet('recipes_app')
    table = spreadsheet.get_worksheet('test01')
    table.insert_headers_from_data(video_data)
    table.insert_rows_from_data(video_data)

if __name__ == "__main__":
    main()