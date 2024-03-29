import os
import json
import random


# Save messages for retrieval later on
def get_recent_messages():
    # Define the file name
    file_name = "stored_data.json"
    learn_instruction = {"role": "system",
                         "content": "You are a receptionist at a doctors clinic and your job is to schedule "
                                    "appointment for the patient based on doctor's availability and take basic "
                                    "details of the patient and your name is Rachel. Keep "
                                    "responses under 30 words. You will be given instructions and in your response do "
                                    "not include the number at the start of the instruction. "}

    # Initialize messages
    messages = []

    # Add Random Element

    learn_instruction["content"] = learn_instruction["content"] + "Your response will be sweet and humble. "


    # Append instruction to message
    messages.append(learn_instruction)

    # Get last messages
    try:
        with open(file_name) as user_file:
            data = json.load(user_file)

            # Append last 5 rows of data
            if data:
                if len(data) < 5:
                    for item in data:
                        messages.append(item)
                else:
                    for item in data[-5:]:
                        messages.append(item)
    except:
        pass

    # Return messages
    return messages


# Save messages for retrieval later on
def store_messages(request_message, response_message):
    # Define the file name
    file_name = "stored_data.json"

    # Get recent messages
    messages = get_recent_messages()[1:]

    # Add messages to data
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    messages.append(user_message)
    messages.append(assistant_message)

    # Save the updated file
    with open(file_name, "w") as f:
        json.dump(messages, f, indent=4)


    # Save messages for retrieval later on
def reset_messages():
    # Define the file name
    file_name = "stored_data.json"

    # Write an empty file
    open(file_name, "w")
