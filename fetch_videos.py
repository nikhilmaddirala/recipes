from googleapiclient.discovery import build
import os
import sqlite3


# Load your API key from an environment variable or secret management service
from dotenv import load_dotenv
load_dotenv()  # This will load the .env file's variables
api_key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

def get_channel_videos(channel_id):
    # Fetch the playlist ID for the channel's videos
    request = youtube.channels().list(part='contentDetails', id=channel_id)
    response = request.execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Fetch videos from the playlist
    videos = []
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()
        
        videos += playlist_response['items']
        next_page_token = playlist_response.get('nextPageToken')
        
        if not next_page_token:
            break
            
    return videos

def create_table():
    conn = sqlite3.connect('youtube_videos.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insert_video_data(channel_id):
    conn = sqlite3.connect('youtube_videos.db')
    cursor = conn.cursor()

    videos = get_channel_videos(channel_id)
    print(f'Found {len(videos)} videos.')

    for video in videos:
        video_id = video['snippet']['resourceId']['videoId']
        title = video['snippet']['title']
        description = video['snippet']['description']
        published_at = video['snippet']['publishedAt']
        
        # Insert a row of data
        cursor.execute("INSERT OR IGNORE INTO videos (video_id, title, description, published_at) VALUES (?, ?, ?, ?)",
                       (video_id, title, description, published_at))

    # Save (commit) the changes
    conn.commit()
    # Close the connection when done
    conn.close()


# Example usage
if __name__ == "__main__":
    create_table()
    remington_james_channel_id = 'UCO9Rhj_x_GgJl-Ria7257EA'  # Replace with the actual channel ID of Remington James
    insert_video_data(remington_james_channel_id)