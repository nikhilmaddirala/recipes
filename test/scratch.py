
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
    "description": "A function that takes in a list of arguments related to a recipe and does something with it",
    "parameters": {
        "type": "object",
        "properties": {
            "title":{
                "type": "string",
                "description":"The title of the recipe, e.g. Creamy Chicken Pasta. Create a title if it is not found in the recipe."
            },
            "ingredients": {
                "type": "array",
                "description": "A list of ingredients with measurable quantities for each ingredient (preferably in grams), together with nutritional information for each ingredient that is estimated based on common nutritional information for the given ingredient and quantity.",
                "items":{
                    "ingredient_name": {"type":"string", "description": "The name of the ingredient, e.g. plain non-fat Greek yogurt"},
                    "quantity":{"type":"string", "description":"The quantity of the ingredient (preferably in grams), e.g. 100 grams"},
                    "calories":{"type":"int", "description":"The number of calories in the ingredient for the specified quantity, e.g. 59"},
                    "protein":{"type":"int", "description":"The grams of protein in the ingredient for the specified quantity, e.g. 10"},
                    "fat":{"type":"int", "description":"The grams of fat in the ingredient for the specified quantity, e.g. 0"},
                    "carbohydrates":{"type":"int", "description":"The grams of carbohydrates in the ingredient for the specified quantity, e.g. 3"},
                    "fiber":{"type":"int", "description":"The grams of fiber in the ingredient for the specified quantity, e.g. 0"}
                    }
                },
            "instructions":{
                "type": "array",
                "description": "The instructions of the recipe broken down into clear, numbered steps.",
            },
            "nutrition":{
                "type": "object",
                "description": "The nutritional information about calories and macronutrients specified in the recipe. If the recipe does not specify nutritional information, leave this field empty.",
                "properties":{
                    "calories":{"type":"int", "description":"The number of calories in the recipe"},
                    "protein":{"type":"int", "description":"The grams of protein in the recipe"},
                    "fat":{"type":"int", "description":"The grams of fat in the recipe"},
                    "carbohydrates":{"type":"int", "description":"The grams of carbohydrates in the recipe"},
                    "fiber":{"type":"int", "description":"The grams of fiber in the recipe"}
                }
            }
        }},
        "required": ["title", "ingredients", "instructions", "instructions"],
    }
