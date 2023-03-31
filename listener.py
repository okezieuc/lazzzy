from dotenv import load_dotenv
import os
import pvporcupine
import time
from twilio.rest import Client
from dotenv import load_dotenv
import os
import pvporcupine
import pyaudio
import struct

load_dotenv()

access_key = os.environ.get("PORCUPINE_ACCESS_KEY")
keywords = ["Okey Zie"]

porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[os.getcwd() + "/bin/Okey-Zie_en_windows_v2_1_0.ppn"],
)


def send_twilio_message(client, recipient, from_):
    message = client.messages.create(
        to=recipient,
        from_=from_,
        body="hey hardworking boss. your attention is needed on the call. someone just called your name.",
    )
    print("reminded my boss")


try:
    # create Twilio client
    twilio_client = Client(
        os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
    )

    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    # initialize time when keyword was last detected to 0
    name_last_detected_at = 0

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print(f"Detected {keywords[keyword_index]}")

            if time.time() - name_last_detected_at > 10:
                name_last_detected_at = time.time()
                # send twilio message here
                send_twilio_message(
                    twilio_client,
                    os.environ.get("TWILIO_RECIPIENT_PHONE_NUMBER"),
                    os.environ.get("TWILIO_FROM_PHONE_NUMBER"),
                )


except KeyboardInterrupt:
    pyaudio.Stream.close(audio_stream)
finally:
    porcupine.delete()
