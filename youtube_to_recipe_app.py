from helpers.youtube_helpers import get_video_id, get_transcript_text
from helpers.llm_helpers import get_recipe_from_llm
import streamlit as st
from dotenv import load_dotenv
import json
import pandas as pd


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
        st.table(ingredients_df)
        st.write('## Instructions')
        st.table(instructions_df)
        st.write('## Nutritional Info')
        st.table(nutritional_info_df)

        st.write('## Full transcript')
        st.write(f'{transcript_text}')
        st.write(f'Video ID: {video_id}')

if __name__ == '__main__':
    main()