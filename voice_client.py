import requests
import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()

print("\n🎤 InsightHost Voice Assistant Started")
print("Speak your question...\n")

while True:

    try:

        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source)

        question = recognizer.recognize_google(audio)

        print("You:", question)

        # send question to FastAPI
        r = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"question": question}
        )

        data = r.json()

        answer = data["answer"]

        print("\nInsightHost:", answer, "\n")

        engine.say(answer)
        engine.runAndWait()

    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")

    except sr.RequestError:
        print("⚠️ Speech recognition service unavailable")

    except Exception as e:
        print("Error:", e)