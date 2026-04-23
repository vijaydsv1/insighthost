from elevenlabs.client import ElevenLabs
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

AUDIO_DIR = "logs/audio_responses"

os.makedirs(AUDIO_DIR, exist_ok=True)


def speak(text):

    if not text:
        return ""

    # limit text size to reduce API cost
    text = text[:300]

    try:

        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2"
        )

        filename = f"response_{uuid.uuid4().hex}.mp3"

        filepath = os.path.join(AUDIO_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        return filepath

    except Exception as e:

        print("⚠️ ElevenLabs TTS error:", e)

        return ""