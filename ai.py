import base64
import os
from openai import OpenAI

API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)

def process(wav_data: bytes) -> bytes:
    encoded_string = base64.b64encode(wav_data).decode('utf-8')

    completion = client.chat.completions.create(
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

    wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    return wav_bytes
