from dotenv import load_dotenv
import os
import pvporcupine
from pvrecorder import PvRecorder

load_dotenv()

access_key = os.environ.get("PORCUPINE_ACCESS_KEY")
keywords = ["Okey Zie"]

porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[os.getcwd() + "/bin/Okey-Zie_en_windows_v2_1_0.ppn"],
)
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
