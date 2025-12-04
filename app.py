import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from assistant import handle_user_prompt
from calendar_integration import create_event_in_calendar

# Load credentials from environment
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    """Twilio webhook: handles inbound call."""
    # Twilio will send speech-to-text transcripts in the 'SpeechResult' field
    user_speech = request.form.get("SpeechResult", "")
    response = VoiceResponse()

    if not user_speech:
        # First prompt to the caller
        response.say("Hello! Thanks for calling. How can I help you today?")
        response.listen()  # gather speech for the next webhook call
        return Response(str(response), mimetype="text/xml")

    # Pass the user's utterance to the assistant
    ai_reply, action = handle_user_prompt(user_speech)

    if action and action.get("type") == "create_appointment":
        # Extract details and schedule an appointment
        date = action["date"]
        time = action["time"]
        title = action.get("title", "Appointment")
        description = action.get("description", "")
        create_event_in_calendar(date, time, title, description)
        response.say(
            f"Got it. I've booked your appointment for {title} on {date} at {time}."
        )
    else:
        # Otherwise just relay the AI response
        response.say(ai_reply)

    # Continue listening in case the caller has more questions
        
    response.listen()
    return Response(str(response), mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
