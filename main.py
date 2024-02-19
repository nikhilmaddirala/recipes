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

def get_recipe_from_assistant(transcript_text):
    """

    Waits for a run to complete and returns the response.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    :return: The response from the assistant.
    """

    assistant = client.beta.assistants.retrieve('asst_2wWfww4gtLttiQspYpGWFfoA')

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=transcript_text
    )

    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    )

    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                # print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(5)

def get_recipe_from_llm(transcript_text):
    """
    Pass recipe and instructions to OpenAI gpt-4-turbo and get recipe
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


def get_recipe_from_url(url):
    video_id = get_video_id(url)
    transcript_text = get_transcript_text(video_id)
    recipe_from_llm = get_recipe_from_assistant(transcript_text)
    return video_id, transcript_text, recipe_from_llm

# Main function to run the program
def main():
    """
    Main function to extract recipe from YouTube video.
    This function prompts the user to enter a YouTube URL, extracts the transcript from the video,
    analyzes the transcript to extract the recipe, and displays the ingredients, instructions, and
    nutritional information of the recipe.
    """
    st.title('Recipe Extractor from YouTube Video')
    with st.form(key='my_form'):
        url = st.text_input('Enter YouTube URL')
        submit_button = st.form_submit_button(label='Submit')

    if url and submit_button:
        # Display a message
        st.text('Extracting transcript from YouTube url...')
        video_id = get_video_id(url)
        transcript_text = get_transcript_text(video_id)

        # Display a message
        st.text('Analyzing transcript to extract recipe...')
        recipe_from_llm = get_recipe_from_llm(transcript_text)
        
        # Convert recipe to datafrmaes
        recipe_dict = json.loads(recipe_from_llm)
        ingredients_df = pd.DataFrame(recipe_dict['ingredients'])
        instructions_df = pd.DataFrame(recipe_dict['instructions'], columns=['Instructions'])
        nutritional_info_df = pd.DataFrame([recipe_dict['nutritional_info']])
        nutritional_info_df = nutritional_info_df.transpose()
        
        st.write('Ingredients:')
        st.dataframe(ingredients_df)
        st.write('Instructions:')
        st.dataframe(instructions_df)
        st.write('Nutritional Info:')
        st.dataframe(nutritional_info_df)


        st.write(f'Video ID: {video_id}')
        st.write(f'Transcript: {transcript_text}')

if __name__ == '__main__':
    main()