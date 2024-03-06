# uvicorn main:app
# uvicorn main:app --reload

# Main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from decouple import config
import openai

# Custom function imports
from functions.text_to_speech import convert_text_to_speech
from functions.openai_request import convert_audio_to_text, get_chat_response
from functions.database import store_messages, reset_messages

# Get Environment Vars
openai.api_key = config("OPEN_AI_KEY")

# Initiate App
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage for doctor availability
doctor_availability = {}


# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}


# Reset Conversation
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"response": "conversation reset"}


# Post bot response
# Note: Not playing back in browser when using post request.
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    # Convert audio to text - production
    # Save the file temporarily
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")

    # Decode audio
    message_decoded = convert_audio_to_text(audio_input)

    # Guard: Ensure output
    if not message_decoded:
        raise HTTPException(status_code=400, detail="Failed to decode audio")

    # Get chat response
    chat_response = get_chat_response(message_decoded, doctor_availability)

    # Store messages
    store_messages(message_decoded, chat_response)

    # Guard: Ensure output
    if not chat_response:
        raise HTTPException(status_code=400, detail="Failed chat response")

    # Convert chat response to audio
    audio_output = convert_text_to_speech(chat_response)

    # Guard: Ensure output
    if not audio_output:
        raise HTTPException(status_code=400, detail="Failed audio output")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Use for Post: Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")


# API endpoint to set doctor availability
@app.post("/set_availability/")
async def set_availability(doctor_name: str, time_slot: str):
    # Parse the time slot string into start and end times
    print("Time slot: ", time_slot)
    start_time_str, end_time_str = time_slot.split("-")
    try:
        start_time = datetime.strptime(start_time_str.strip(), "%I%p")
        end_time = datetime.strptime(end_time_str.strip(), "%I%p")
        print("Start time: ", start_time)
        print("End time: ", end_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time slot format")

    # Check if doctor ID already exists
    if doctor_name in doctor_availability:
        doctor_availability[doctor_name].append((start_time, end_time))
    else:
        doctor_availability[doctor_name] = [(start_time, end_time)]

    print("Doctor availability: ", doctor_availability)
    return {"message": "Availability set successfully"}
