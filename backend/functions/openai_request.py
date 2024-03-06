import openai
from decouple import config
from openai import OpenAI

from functions.database import get_recent_messages

client = openai.Client(api_key=config("OPEN_AI_KEY"))


# Open AI - Whisper
# Convert audio to text
def convert_audio_to_text(audio_file):
    print("Called convert_audio_to_text")
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        message_text = transcript.text
        print("Converted audio to text: " + message_text)
        return message_text
    except Exception as e:
        print(e)
        return


# Open AI - Chat GPT
# Convert audio to text
def get_chat_response(message_input, doctor_availability):
    if not message_input:
        return "Error: Message input cannot be empty."

    messages = get_recent_messages()

    if not messages:
        messages = []

    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    # Add doctor availability context
    availability_message = {"role": "system", "content": "Doctor availability:"}
    for doctor_name, slots in doctor_availability.items():
        availability_message["content"] += f"\nDoctor {doctor_name}:"
        for start_time, end_time in slots:
            availability_message[
                "content"] += f"\n- {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

    messages.append(availability_message)
    print(messages)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        message_text = response.choices[0].message.content
        return message_text
    except Exception as e:
        print(e)
        return
