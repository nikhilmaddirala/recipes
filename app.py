from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = ""
    recipe = ""  # Initialize recipe
    if request.method == 'POST':
        youtube_url = request.form['url']
        video_id = youtube_url.split('v=')[1]  # Extract video ID from URL
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([x['text'] for x in transcript])

        # Read instructions from file
        with open('instructions.txt', 'r') as file:
            instructions = file.read()

        # Pass the transcript text to the OpenAI Assistant API
        response = client.chat.completions.create(model="gpt-4-turbo-preview",
        messages=[
              {"role": "system", "content": instructions},
              {"role": "user", "content": transcript_text}
          ])

        # Extract the assistant's reply
        recipe = response.choices[0].message.content

    return render_template('index.html', transcript=transcript_text, recipe=recipe)

if __name__ == "__main__":
    app.run(debug=True)