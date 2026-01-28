# calibration.py

# %% imports
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import json
import matplotlib.pyplot as plt
import os
from scipy import stats

from .utils import read_json

# %% Calibraiton functions


def start_calibrating(channelNr: int, start, stop, increment):

    if channelNr != 0 and channelNr != 1:
        raise ValueError("channelNR must be either 0 or 1")

    ai_channels = ["Dev1/ai0", "Dev1/ai1"]
    with nidaqmx.Task() as task:
        # Configure the AI channel
        task.ai_channels.add_ai_voltage_chan(
            ai_channels[channelNr], terminal_config=TerminalConfiguration.RSE)

        keepCalibrating = True
        calibrationData = {}

        degreeValues = []
        voltValues = []

        i = start
        while i <= stop + 1e-9:  # avoids floating point edge issues
            input(f"Set the sensor to {i:.1f} and press Enter...")

            voltage = task.read()

            degreeValues.append(i)
            voltValues.append(voltage)

            i += increment

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
        fullFilename = f"calibration_files/CallibrationReportPotmeter{
            str(channelNr)}.json"
        with open(fullFilename, "w") as outfile:
            outfile.write(jsonData)

        print(f"CallibrationReport saved as '{fullFilename}'")


def calc_linear_regression(deg90Pot0, deg90Pot1):

    dataPot0 = read_json("calibration_files/CallibrationReportPotmeter0.json")
    dataPot1 = read_json("calibration_files/CallibrationReportPotmeter1.json")
    slopePot0, _, _, _, _ = stats.linregress(dataPot0['voltValues'],
                                             dataPot0['degreeValues'])
    slopePot1, _, _, _, _ = stats.linregress(dataPot1['voltValues'],
                                             dataPot1['degreeValues'])

    intercept0 = deg90Pot0[0] - (slopePot0 * deg90Pot0[1])
    intercept1 = deg90Pot1[0] - (slopePot1 * deg90Pot1[1])

    return (slopePot0, intercept0), (slopePot1, intercept1)


def calc_intercept(ai_channel, inputValue):

    ai_channels = ["Dev1/ai0", "Dev1/ai1"]

    with nidaqmx.Task() as task:
        # Configure the AI channel
        task.ai_channels.add_ai_voltage_chan(
            ai_channels[ai_channel], terminal_config=TerminalConfiguration.RSE)
        zeroPoint = task.read()

    return (inputValue, zeroPoint)
