
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


function = {
    "name": "recipe_metadata",
    "description": "A function that takes in a list of arguments related to a children's story and does something with it",
    "parameters": {
        "type": "object",
        "properties": {
            "title":{
                "type": "string",
                "description":"The title of the story"
            },
            "story_text":{
                "type": "string",
                "description":"The text of the story"
            },
            "top_5_words": {
                "type": "array",
                "description": "A list of the 5 hardest words in the story along with its definition.",
                "items":{
                    "word": {"type":"string", "description": "A difficult word in the story"},
                    "definition":{"type":"string", "description":"The dictionary definition for the word",
                    "sample_use":{"type":"array", "description": "a list of two sample sentences showing how this word can be used."}
                    }
                },
            "word_count":{
                "type": "int",
                "description": "The total number of words in this story",
            }
        }}},
        "required": ["title", "story_text", "top_5_words", "word_count"],
    }
