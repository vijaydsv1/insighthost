from speech.stt import listen
from speech.tts import speak
from pipeline.assistant_pipeline import run_assistant


WAKE_WORD = "insight host"


def start_voice_assistant():

    speak("Hello, I am InsightHost. Say Hey InsightHost to start.")

    while True:

        text = listen()

        if not text:
            continue

        text = text.lower()

        if WAKE_WORD in text:

            speak("Hello. How can I help you?")

            query = listen()

            if not query:
                continue

            response = run_assistant(query)

            speak(response)

        elif "exit" in text or "stop" in text:

            speak("Goodbye")

            break


if __name__ == "__main__":
    start_voice_assistant()