from io import BytesIO
import wave
import pyaudio
import base64
import os
from openai import OpenAI
from gpiozero import Button

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

API_KEY = os.environ['OPENAI_API_KEY']
CLIENT = OpenAI(api_key=API_KEY)

BUTTON = Button(2)

def stop_recording():
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

def process(wav_data: bytes) -> bytes:
    encoded_string = base64.b64encode(wav_data).decode('utf-8')

    completion = CLIENT.chat.completions.create(
        model='gpt-4o-audio-preview',
        modalities=['text', 'audio'],
        audio={"voice": "echo", "format": "wav"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encoded_string,
                            "format": "wav"
                        }
                    }
                ]
            }
        ]
    )

    print(completion.choices[0].message.audio.transcript)
    wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    return wav_bytes

BUTTON.when_released = stop_recording
while True:
    BUTTON.wait_for_press()
    play_response(process(record()))
