from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    youtube_url = data['url']
    video_id = youtube_url.split('v=')[1]  # Extract video ID from URL
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([x['text'] for x in transcript])
    return jsonify({'transcript': transcript_text}), 200

if __name__ == "__main__":
    app.run(debug=True)