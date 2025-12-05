
# MovementAmplitudeFeedbackDAQ
## A toolbox for measuring rhythmical coordination
This toolbox was developed for a master’s research project investigating how people coordinate rhythmic movements with different movement amplitudes.

Two potentiometers were attached to rotating elbow rests to measure the angular position of each limb over time. Using this setup, the toolbox measures the voltage signals from both potentiometers, computes the movement amplitude for each rhythmic cycle, and provides participants with near real-time visual feedback about their performance — all while indicating the frequency of the rhythmic movements with an audio metronome.

This makes the toolbox suitable for a wide range of rhythmic coordination tasks using potentiometers. 

## Technical explanation

The voltage of these potentiometers is measured with a USB-6009 device from National Instruments. The USB-6009 should be connected to the PC. Potentiometers 1 and 2 should be connected to ports AI0 and AI1, respectively.

Before running a measurement with this toolbox, a few functions need to be executed. 

### calibration

Before starting any measurements, the potentiometers need to be calibrated so that the output voltage can be linked to angles in degrees. Note that only linear potentiometers can be used with this toolbox.

Calibration can be done with the startCalibration function located in calibration.py. An example of how to run this calibration can be found in example_calibration.py in the main folder. This function records the voltages at a set of known angle positions and then calculates the slope using a linear regression.

### initiate class from measurement.py

After both potentiometers are calibrated, initiate the class from measurement.py. An example of this is provided in example_usage.py.

### calculate 90 degree point

It is possible that the potentiometers shift slightly in the elbow rest. Before starting a set of measurements, calculate the 90-degree point of each potentiometer using the calcPointZero() method in measurement.py. An example is provided in example_usage.py.

### Metronome




### start measuring

Now you can start a measurement. Run the startMeasuring method in the Spyder console. The operator will see the raw signal from both potentiometers, while the participant will see the feedback figure and hear the metronome. When the spacebar is pressed, the measurement will begin.

You can rerun startMeasuring in the console for additional measurements. The script will automatically save each trial as a separate .json file.


## how to install

Open the **anaconda prompt** and run:

```bash
conda env create -f nidaqmx_env.yml
```
Then activate the environment:

```bash
conda activate nidaqmx_env
```
Now install the drivers for nidaqmx toolbox:

```bash
python -m nidaqmx installdriver
```

The driver installation can only be done while the nidaqmx_env environment is active.


## Spyder settings

When first opening Spyder, adjust the following setting:

Go to Preferences → IPython Console → Graphics and set the backend to QT5.

## Toolbox development

The following items are on the agenda for future development:

    1. A GUI to make the toolbox more user-friendly

    2. Support for measuring signals from sensors other than potentiometers, such as FSRs
