from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os
import logging
import time

def get_recipe_from_llm(transcript_text):
    """
    Pass recipe and instructions to OpenAI and get recipe
    """

    # Load .env file
    load_dotenv()

    # client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # read system instructions from instructions.txt
    with open('llm_prompts/instructions.txt', 'r', encoding='utf-8') as file:
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

