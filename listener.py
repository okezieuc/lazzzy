from dotenv import load_dotenv
import os
import pvporcupine
from pvrecorder import PvRecorder

load_dotenv()

access_key = os.environ.get("PORCUPINE_ACCESS_KEY")

keywords = ["picovoice", "bumblebee"]

porcupine = pvporcupine.create(access_key=access_key, keywords=keywords)
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)


try:
    recoder.start()

    while True:
        keyword_index = porcupine.process(recoder.read())
        if keyword_index >= 0:
            print(f"Detected {keywords[keyword_index]}")


except KeyboardInterrupt:
    recoder.stop()
finally:
    porcupine.delete()
    recoder.delete()
