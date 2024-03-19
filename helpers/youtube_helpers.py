import re
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url, fuzzy=True):
    """Extracts YouTube video ID from a variety of URL formats."""
    patterns = [
        r"youtu\.be/([^#\&\?]{11})",  # youtu.be/<id>
        r"\?v=([^#\&\?]{11})",        # ?v=<id>
        r"\&v=([^#\&\?]{11})",        # &v=<id>
        r"embed\/([^#\&\?]{11})",      # embed/<id>
        r"/v/([^#\&\?]{11})"          # /v/<id>
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if fuzzy:
        tokens = re.split(r"[#\&\?=/\s]", url)  # More flexible splitting
        for token in tokens:
            if re.match(r"^[^#\&\?]{11}$", token):
                return token
    return None

def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([x['text'] for x in transcript])
        return transcript_text
    except Exception as e:
        return f"An error occurred while retrieving the transcript for this video. Error: {str(e)}"
