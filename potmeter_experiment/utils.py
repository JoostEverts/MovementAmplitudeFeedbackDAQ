# utils.py

import json

import numpy as np
import wave
import sounddevice as sd
import os

def read_json(filename):
    fullFilename = filename +'.json'
    with open(fullFilename, "r") as openfile:
        json_data = json.load(openfile)

    return(json_data)


def play_sound(metronomeFile):
    with wave.open(metronomeFile, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        dtype = np.int16
        frames = wav_file.readframes(wav_file.getnframes())
        audio_data = np.frombuffer(frames, dtype=dtype)
        if channels > 1:
            audio_data = np.reshape(audio_data, (-1, channels))
        sd.play(audio_data, samplerate=sample_rate, loop=True)

def check_nidaqmx_connected():
    
    import nidaqmx.system
    system = nidaqmx.system.System.local()
    devices = system.devices.device_names
    if len(devices) == 0:
        raise RuntimeError("No NI-DAQmx devices detected. Please connect your device.")
    else:
        print("NI-DAQmx device is connected")
        
def check_callibration_available():
    
    if (
    os.path.exists("./calibration_files/CallibrationReportPotmeter0.json")
    and os.path.exists("./calibration_files/CallibrationReportPotmeter1.json")
    ):
        print("Calibration files are ready")
        
    else:
        raise FileNotFoundError("Calibration file(s) not found. " 
                                "Calibrate the potentiometers using calibration.py in the toolbox!")