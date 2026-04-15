import requests
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
recognizer = sr.Recognizer()

while True:

    with sr.Microphone() as source:
        print("Speak...")
        audio = recognizer.listen(source)

    try:
        question = recognizer.recognize_google(audio)
        print("You:", question)

        r = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"question": question}
        )

        answer = r.json()["answer"]

        print("Assistant:", answer)

        engine.say(answer)
        engine.runAndWait()

    except:
        print("Could not understand")