import os
from googleapiclient.discovery import build
from supabase_py import create_client, Client
import re
from dotenv import load_dotenv

load_dotenv()

def create_youtube_client():
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    return youtube

def create_supabase_client():
    url: str = os.getenv('SUPABASE_URL')
    anon_key: str = os.getenv('SUPABASE_ANON_KEY')
    supabase: Client = create_client(url, anon_key)
    return supabase

def get_channel_id(channel_url):
    return re.search('channel/([a-zA-Z0-9_-]+)', channel_url).group(1)

def get_videos(youtube, channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50,  # Change this number to get more videos
        type='video'
    )
    return request.execute()

def insert_videos(supabase, videos):
    for item in videos['items']:
        video = {
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt']
        }
        supabase.table('videos').insert(video)

def main():
    youtube = create_youtube_client()
    supabase = create_supabase_client()
    channel_url = input('Enter the YouTube channel URL: ')
    channel_id = get_channel_id(channel_url)
    videos = get_videos(youtube, channel_id)
    print(videos)
    # insert_videos(supabase, videos)

if __name__ == "__main__":
    main()