import ai
from io import BytesIO
import wave
import sys
import pyaudio
import threading

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == 'darwin' else 2
RATE = 44100

def wait_for_recording():
    input("Recording, press enter to proceed...\n")
    global running
    running = False

def record() -> bytes:
    global running
    data = BytesIO()

    with wave.open(data, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        running = True

        input_thread = threading.Thread(target=wait_for_recording)
        input_thread.daemon = True
        input_thread.start()

        while running:
            wf.writeframes(stream.read(CHUNK))

        stream.close()
        p.terminate()

    return data.getvalue()

def play_response(output: bytes):
    with wave.open(BytesIO(output), 'rb') as wf:
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        while len(data := wf.readframes(CHUNK)):
            stream.write(data)

        stream.close()
        p.terminate()

play_response(ai.process(record()))
