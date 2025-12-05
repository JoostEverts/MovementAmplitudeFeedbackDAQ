# calibration.py

import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import json
import matplotlib.pyplot as plt
import os
from .utils import read_json
from scipy import stats

def startCalibrating(channelNr: int):
    
    if channelNr != 0 and channelNr != 1:
        raise ValueError("channelNR must be either 0 or 1")
    
    ai_channels = ["Dev1/ai0", "Dev1/ai1"]
    with nidaqmx.Task() as task: 
        # Configure the AI channel
        task.ai_channels.add_ai_voltage_chan(ai_channels[channelNr], terminal_config= TerminalConfiguration.RSE)
        
        keepCalibrating = True
        calibrationData = {}
        
        start = 40
        stop = 140
        increment = 10
        degreeValues = []
        voltValues = []
        
        for i in range(start, stop+increment, increment):
            
            calibrationInput = input(f"Set the elbowrest to {i} degrees and press Enter...")
            
            degreeValues.append(i)
            voltValues.append(task.read())
                
        
        
        plt.figure()
        plt.plot(voltValues, degreeValues)
        plt.plot(voltValues, degreeValues, "r*")
        plt.xlabel("voltage values")
        plt.ylabel("degree values")
        plt.title("Calibration Data")
        
        calibrationData['degreeValues'] = degreeValues
        calibrationData['voltValues'] = voltValues
        
        os.makedirs("potmeter_experiment", exist_ok=True)
        
        jsonData = json.dumps(calibrationData)
        fullFilename = f"calibration_files/CallibrationReportPotmeter{str(channelNr)}.json"
        with open(fullFilename, "w") as outfile:
            outfile.write(jsonData)
        
        print(f"CallibrationReport saved as '{fullFilename}'")
        

def calc_linear_regression(deg90Pot1, deg90Pot2):
    
    dataPot1 = read_json("calibration_files/CallibrationReportPotmeter0")
    dataPot2 = read_json("calibration_files/CallibrationReportPotmeter1")
    slopePot1, _, _, _, _ = stats.linregress(dataPot1['voltValues'],
                                                      dataPot1['degreeValues'])
    slopePot2, _, _, _, _ = stats.linregress(dataPot2['voltValues'],
                                                      dataPot2['degreeValues'])
    
    intercept1 = 90 - (slopePot1 * deg90Pot1)
    intercept2 = 90 - (slopePot2 * deg90Pot2)

    return (slopePot1, intercept1), (slopePot2, intercept2)


def convert_degree_to_volt():
    pass






