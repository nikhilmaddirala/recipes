from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import logging
import time
import json
import pandas as pd

# Load .env file
load_dotenv()

# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_video_id(url):
    video_id = url.split('v=')[1]  # Extract video ID from URL
    return video_id

def get_transcript_text(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([x['text'] for x in transcript])
    return transcript_text

def get_recipe_from_llm(transcript_text):
    """
    Pass recipe and instructions to OpenAI and get recipe
    """

    # read system instructions from instructions.txt
    with open('instructions.txt', 'r', encoding='utf-8') as file:
        system_instructions = file.read()

    messages = []

    messages.append({
        "role": "system",
        "content": system_instructions
    })

    messages.append({
        "role": "user",
        "content": transcript_text
    })

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

    recipe_from_llm = response.choices[0].message.content
    return recipe_from_llm


# Main function to run the program
def main():
    """
    Main function to extract recipe from YouTube video.
    This function prompts the user to enter a YouTube URL, extracts the transcript from the video,
    analyzes the transcript to extract the recipe, and displays the ingredients, instructions, and
    nutritional information of the recipe.
    """
    st.title("Nikhil\'s YouTube recipe extractor")
    with st.form(key='my_form'):
        url = st.text_input('Enter YouTube URL')
        submit_button = st.form_submit_button(label='Submit')

    if url and submit_button:
        # Get transcript
        st.text('Extracting transcript from YouTube url...')
        video_id = get_video_id(url)
        transcript_text = get_transcript_text(video_id)

        # Extract recipe
        st.text('Analyzing transcript to extract recipe...')
        recipe_from_llm = get_recipe_from_llm(transcript_text)
        st.text('Done! Here is the recipe:')
        
        # Convert recipe to datafrmaes
        recipe_dict = json.loads(recipe_from_llm)
        ingredients_df = pd.DataFrame(recipe_dict['ingredients'])
        instructions_df = pd.DataFrame(recipe_dict['instructions'], columns=['Instructions'])
        nutritional_info_df = pd.DataFrame([recipe_dict['nutritional_info']])
        nutritional_info_df = nutritional_info_df.transpose()
        
        st.write('## Ingredients')
        st.dataframe(ingredients_df)
        st.write('## Instructions')
        st.dataframe(instructions_df)
        st.write('## Nutritional Info')
        st.dataframe(nutritional_info_df)

        st.write('## Full transcript')
        st.write(f'{transcript_text}')
        st.write(f'Video ID: {video_id}')

if __name__ == '__main__':
    main()