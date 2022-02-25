from vosk import Model, KaldiRecognizer
import sys
import os
import wave
import subprocess
import json
import time


class Transcriber:
    sample_rate = 16000

    def __init__(self, model_path, file_path):
        if not os.exists(file_path):
            print(
                "Please download a model from https://alphacephei.com/vosk/models and unpack it as 'model' in the provided folder."
            )
            sys.exit(1)

        self.file_path = file_path

        self.model_path = model_path
        self.model = Model(model_path)

        self.rec = KaldiRecognizer(self.model, self.sample_rate)
