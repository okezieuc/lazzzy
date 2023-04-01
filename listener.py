from dotenv import load_dotenv
import os
import pvporcupine
import time
from twilio.rest import Client
from dotenv import load_dotenv
import os
import pvporcupine
import pyaudiowpatch as pyaudio
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

    # function that creates default wasapi device
    def get_default_wasapi_device(p_audio: pyaudio.PyAudio):
        try:  # Get default WASAPI info
            wasapi_info = p_audio.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("Looks like WASAPI is not available on the system")
            exit()

        # Get default WASAPI speakers
        sys_default_speakers = p_audio.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"]
        )

        if not sys_default_speakers["isLoopbackDevice"]:
            for loopback in p_audio.get_loopback_device_info_generator():
                if sys_default_speakers["name"] in loopback["name"]:
                    return loopback
                    break
            else:
                print(
                    "Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices"
                )
                exit()

    """
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )
    """

    # set target device for stream
    target_device = get_default_wasapi_device(pa)

    print("target: ", target_device)

    print(porcupine.sample_rate)

    audio_stream = pa.open(
        format=pyaudio.paInt16,
        # channels=target_device["maxInputChannels"],
        channels=1,
        rate=porcupine.sample_rate,
        # frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt24),
        frames_per_buffer=porcupine.frame_length,
        input=True,
        input_device_index=target_device["index"],
        # stream_callback=self.callback,
    )

    # initialize time when keyword was last detected to 0
    name_last_detected_at = 0

    while True:
        # print('listening')
        # pcm = audio_stream.read(pyaudio.get_sample_size(pyaudio.paInt24))
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        # print('checkpoint: 1')
        # print(pcm)
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
        # else:
        # print('not detected')


except KeyboardInterrupt:
    pyaudio.Stream.close(audio_stream)
finally:
    porcupine.delete()
