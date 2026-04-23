import speech_recognition as sr


def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("\n🎤 Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        except sr.WaitTimeoutError:
            print("⚠️ No speech detected")
            return None

    try:

        text = recognizer.recognize_google(
            audio,
            language="en-US"
        )

        print(f"You: {text}")

        return text

    except sr.UnknownValueError:

        print("⚠️ Could not understand audio")

        return None

    except sr.RequestError:

        print("⚠️ Speech recognition service unavailable")

        return None