
# MovementAmplitudeFeedbackDAQ
## A toolbox for measuring rhythmical coordination
This toolbox was developed for a master’s research project in Human Movement Sciences investigating how people rhythmically coordinate with different movement amplitudes.

Using this setup, the toolbox measures the voltage signals from both sensors of the left and right limb, computes the movement amplitude for each rhythmic cycle, and provides participants with near real-time visual feedback about their performance — all while indicating the frequency of the rhythmic movements with an audio metronome.

Originally, two potentiometers were used to measure the angular position of each limb over time. However, this toolbox can also be used with other sensors, such as slide potentiometers or Force-Sensitive Resistors.

This flexibility makes the toolbox suitable for measuring a wide range of rhythmic coordination tasks. 

## Technical explanation

The voltage of these potentiometers is measured with a USB-6009 device from National Instruments. The USB-6009 should be connected to the PC via USB. The sensors of limb 1 and limb 2 should be connected to ports AI0 and AI1. The sensors should be attached to each limb so that the rhythmical movements can be measured. Note that this script can only detect peaks of rhythmical ongoing movements.

This toolbox was developed in Spyder using Anaconda. This readme will explain how to install the packages and run this script in Spyder. This may differ for other Python interpreters. 

### Peak detection algorithm

To detect the peaks, we used a simple but robust algorithm. This means that the algorithm does not take much computing time, though it may have a measuring error of a couple of frames. One of its main advantages is that it can calculate the amplitude just one frame after a rhythmic cycle, allowing for fast feedback to the participant.

The algorithm detects peaks in several steps:

1. Thresholded slope detection

The slope is calculated. An ascending slope that exceeds a defined threshold is identified. Then the script looks for a corresponding descending slope. Both indices are stored for the next step.


2. Peak detection

The peak is detected by taking the index in the middle of the saved ascending and descending slopes. This method may introduce a small error of a few frames but reduces computation time.

3. Amplitude calculation

Once two peaks are found (a maximum and a minimum), the amplitude is calculated by the difference between the maximum and minimum values.


### Measuring and visualisation 

Measurement and visualisation (along with peak detection) are two processes that run at the same time during a measurement. The NI-DAQmx device measures 5 frames per batch at a specified sample rate. The visualisation and peak detection tasks are performed at approximately 20 frames per second. To achieve this, the most recent sample from the measurement is used each frame to update the feedback.

## Files

The toolbox contains 4 main folders in the root directory:

1. Calibration_files

This folder stores the results of the calibration (from calibrationScript.py). It also contains a file that saves previous settings of the main script.

2. Measurement_files

Contains the raw measurement data.

3. Measurement_toolbox

Includes all the Python scripts used in the toolbox.

4. Metronome_files

Stores audio files for the metronome. When a metronome filename is entered in the main script settings, the script will search for this file in this folder.

Additionally, there are 5 important files in the root folder:

1. anaconda_environment.yml

Use this file to install an Anaconda environment with the correct packages for running the scripts.

2. calibrationScript.py

Script used to calibrate the sensors.

3. example_excel_experiment.xlsx

Excel file to store measurement settings for a full experiment for one participant.

4. measurementScripts.py

Script used to run the main experiment.

5. designFeedbackFigure.py

Script that can be used to quickly design the feedback figure by changing parameters by trial-and-error. Later, these parameters can be entered into the General Settings GUI when running measurementScript.py.

## How to install the packages in Anaconda

To use this module in Anaconda, Anaconda needs to be downloaded, an environment with the necessary modules needs to be installed and drivers for nidaqmx need to be installed.

First, download Anaconda at Anaconda.org.

Then, open the **Anaconda prompt**, change the directory of the prompt to the location of the 'anaconda_environment.yml' file, which is provided in the toolbox and run:

```bash
conda env create -f anaconda_environment.yml
```
Next, activate the environment:

```bash
conda activate AmplitudeFeedbackDAQ_env
```
Now install the drivers for NI-DAQmx toolbox:

```bash
python -m nidaqmx installdriver
```
When prompted, type **y** to finish the installation.

A window pops up where you can check which driver installations you want to install.

You only need to install: **NI-DAQmx Support for C**.

The driver installation can only be done while AmplitudeFeedbackDAQ_env environment is active.

## Spyder settings

Open Spyder by activating the AmplitudeFeedbackDAQ_env environment again: 

```bash
conda activate AmplitudeFeedbackDAQ_env
```

And opening Spyder by running the following command in the Anaconda prompt:

```bash
spyder
```

Before you can use Spyder to run this toolbox, a couple of settings need to be adjusted:

1. Backend setup

Go to Preferences → IPython Console → Graphics and set the backend to QT5.

## How to Use this toolbox

This toolbox can be used with two scripts located in the root directory:

1. calibrationScript.py
2. measurementScript.py

The use of both scripts is described below.

### calibrationScript.py

Before starting any measurements, the sensors connected to AI0 and AI1 need to be calibrated so that the output voltage can be linked to an input value. This is done with the calibrationScript.py script inside the toolbox. Completing the calibration will result in two calibration files, which are later used when doing measurements. Note that at the moment only linear sensors can be used with this toolbox.

Make sure the right calibration files are stored inside the calibrationfolder. The script will also run with outdated calibration files and will give wrong feedback values.

### measurementScript.py

This script has three main functions:
1. It generates a main GUI to alter the general settings.
2. It generates a GUI with measurement specific settings (these can be manually entered or with the use of an excel file).
3. It starts measurements.

The script repeats steps 2 and 3 until the measurement GUI is closed.

#### The main GUI

When the calibrationScript.py script is started, the main GUI will pop up. Here, several parameters can be adjusted.

Two general settings variables:

1. The name of the participant --> string

A folder is created in participant_files with this name, storing all measurement .json files.

2. Sample frequency --> int

Sample frequency in frames/second

Four settings which influence the amplitude feedback figure which participants will get to see:

1. Maximum amplitude

The highest value the movement can reach. Sets the top of the feedback scale.

2. Minimum amplitude

The lowest value the movement can reach. Sets the bottom of the feedback scale.

3. Target amplitude height

The vertical size of the target area on the feedback plot.

4. Feedback bar width

Thickness of the bar that shows your current movement amplitude on the plot.

##### Calculate calibration offset

Some sensors, like potentiometers, may shift within a measurement setup. For example, 90° in the system might correspond to different output voltages depending on the sensor position. To correct for this, the calibration offset can be recalculated while keeping the sensor slope constant.

Steps:

1. Set the sensor to a known input value (e.g., 90°).
2. Enter this value in the Input Value box for the corresponding channel.
3. Click Calculate Offset Channel X.

If this function is not used, the system will use the offset from the previous measurement.

##### Excel file checkbox

It is possible to run experiments with predefined settings across multiple trials using an Excel file:

Check the Excel File checkbox and press Submit.

Select the experiment Excel file.

**Important:** Do not change the header names in the Excel file, as the script relies on them to read the measurement settings. An example Excel file is provided in the toolbox.

#### Measurement GUI parameters

After the main GUI, the measurement settings GUI appears. Here, you can enter trial-specific measurement settings.

If you use an excel file for your experiment, these settings cannot be altered. The only thing that can be altered is the trial number with the button **Change trial number**. Changing the trial number will automatically change your measurement settings. 

When you do not use an excel file for your experiment, or the current trial number exceeds the number of trials in your Excel file, you can manually enter the measurement settings. The following settings can then be altered:

1. right target amplitude --> float

This is the target amplitude for the right limb which the participant is aiming to produce.

2. left target amplitude --> float

This is the target amplitude for the left limb which the participant is aiming to produce.

3. trial duration --> float

This is the trial duration in seconds.

4. metronome duration --> float

Duration the metronome will play after the trial starts. Useful for experiments where rhythmic pacing is provided at the start and then removed to minimize metronome influence.

5. Metronome filename --> string

The audio filename of the metronome (with extension included). This audio file should be located in the metronome_files folder.

#### Start measurement

When the settings are entered, press **start measuring**. 

A graph will appear with the raw signal of the two sensors for the operator, and a feedback graph appears for the participant. At the same time the metronome will start beeping. When it is time to start the measurement, press **spacebar**. 
The metronome will stop after the specified duration, and the measurement will end after the given trial duration. The trial can also be stopped prematurely by closing the window with the raw signal.
After a trial ends, the measurement settings window reappears for the next trial. Closing this window ends the entire measurement session.

