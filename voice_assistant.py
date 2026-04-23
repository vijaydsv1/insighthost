import pvporcupine
import pyaudio
import struct

from rag.rag_chain import get_rag_response
from speech.tts import speak
from speech.stt import listen


def start_voice_assistant():

    print("🎤 Voice assistant started")
    print("Say: 'Hey InsightHost'")

    porcupine = pvporcupine.create(
        keywords=["computer"]  # wake word (closest to "hey insighthost")
    )

    pa = pyaudio.PyAudio()

    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    while True:

        pcm = stream.read(porcupine.frame_length)

        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        result = porcupine.process(pcm)

        if result >= 0:

            print("\n👂 Wake word detected")

            speak("Hello, I am InsightHost. How can I help you?")

            query = listen()

            if not query:
                speak("Sorry, I could not hear you.")
                continue

            print("User:", query)

            answer = get_rag_response(query)

            print("InsightHost:", answer)

            speak(answer)