# measurement.py

import collections
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
import sounddevice as sd
import time
import keyboard
from .utils import read_json, play_sound, check_nidaqmx_connected, check_callibration_available # helper functions
import os
import json
from .calibration import calc_linear_regression

#%% class
class PotmeterMeasurement:
    
    def __init__(self, participantName, leftTarget, rightTarget, fs, duration, filenameMetronome, metronomeDuration):
        
        self.participantName = participantName
        
        # target trial
        self.leftTargetDeg = leftTarget
        self.rightTargetDeg = rightTarget
        
        # measuring settings
        self.sampleFrequency = fs
        self.duration = duration
        self.trialNr = 1
        
        # 90 degree angle voltage placeholder
        self.pot0ZeroPoint = None
        self.pot1ZeroPoint = None
        
        # metronome settings
        self.metronomeFile = filenameMetronome
        self.metronomeDuration = metronomeDuration
        
        # create data storage attributes
        self.dataPot1 = collections.deque()
        self.dataPot2 = collections.deque()
        
        # calculate slope potentiometers
     
    @classmethod
    def instantiateWithMeasurementFile(cls, filename, foldername):
        
        data = read_json(foldername + '/' + filename)
        instance = cls(foldername, data["leftTarget"], data["rightTarget"], data["sampleFrequency"], data["duration"])
        instance.pot0ZeroPoint = data["ZeroPointPotmeter0"]
        instance.pot1ZeroPoint = data["ZeroPointPotmeter1"]
        instance.trialNr = int(filename[6:]) + 1
        return instance
    
    def data_acquisition(self, fs, duration, e):
        
        # function to start the data acquisition. Inputs are the sampling frequentie (fs)
        # and the acquisition duration in seconds (duration). Fuction returns an array with the data.
        
        self.dataPot1.clear()
        self.dataPot2.clear()
        
        
        samples_per_read = 5  # Number of samples per read (1/3rd of a second)
        ai_channels = ["Dev1/ai0", "Dev1/ai1"]
        
        with nidaqmx.Task() as task2: 
            # Configure the AI channel
            task2.ai_channels.add_ai_voltage_chan(ai_channels[0], terminal_config= TerminalConfiguration.RSE)
            task2.ai_channels.add_ai_voltage_chan(ai_channels[1], terminal_config= TerminalConfiguration.RSE)
            
            # Configure the sampling timing
            task2.timing.cfg_samp_clk_timing(
                rate=fs, 
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=samples_per_read  # Buffer size for continuous acquisition
            )
            
            # Prepare a buffer to hold the data with correct shape (channels, samples_per_read)
            data = np.zeros((2, samples_per_read))
            # data_total = []
            
            # Create the stream reader
            reader = AnalogMultiChannelReader(task2.in_stream)
            
            # Start the task
            e.wait() # waiting for plot setup in data_visualisation function
            
            print("start reading")
            task2.start()
            self.timeStart = 0
            endTime = 0
            starting = False
            
            # Continuously read data until the duration elapses
            while e.is_set() and not starting:
                reader.read_many_sample(data, number_of_samples_per_channel=samples_per_read, timeout=10.0)
                self.dataPot1.extend(data[0,:])
                self.dataPot2.extend(data[1,:])
                # Read data into the buffer
                # print('reading data.....')
                if keyboard.is_pressed("space"):
                    print("Measurement started")
                    self.timeStart = time.time()
                    endTime = time.time() + self.duration
                    starting = True
                    
            
            print("start second loop")
            while e.is_set and endTime - time.time() >= 0:
                reader.read_many_sample(data, number_of_samples_per_channel=samples_per_read, timeout=10.0)
                self.dataPot1.extend(data[0,:])
                self.dataPot2.extend(data[1,:])
                
                if endTime - time.time() < self.duration-self.metronomeDuration:
                    sd.stop()
                
                
            
            timeNeeded = time.time() - self.timeStart
            e.clear()
            # Stop the task
            task2.stop()
            
            print(f"Acquisition time: {timeNeeded} seconds")   
        #return np.array(self.dataPot1), np.array(self.dataPot2)

    def data_visualisation(self, left_target_A, right_target_A, e):
        
        # function visualizes data from two potmeters. determines the minimum and mixima of the signal.
        # then calculates the amplitude and plots it.
        
        treshold = 0.05 # the lower this threshold the higher the sensitivity for finding peaks.
        max_amplitude = 2.5
        targetHeight = 0.3
        
        def findTreshold(potValue, previousPotValue, treshold):
            
            if potValue - previousPotValue > treshold:
                diffValue = 1
            elif potValue - previousPotValue < -treshold:
                diffValue = -1
            else:
                diffValue = 0
                
            return diffValue
        
        # setup Potentiometer data plot
        plt.close('all')
        plt.ion()
        
        # Setup raw signal plot
        fig1, ax1 = plt.subplots()
        ax1.set_ylim((0, 5))
        ax1.set_xlim((0, 100))
        
        ax1.plot([], [], 'b-')
        ax1.plot([], [], 'ko')
        
        ax1.plot([], [], 'r-')
        ax1.plot([], [], 'ko')
        
        # Setup online feedback plot
        fig2, ax2 = plt.subplots()
        manager = plt.get_current_fig_manager()
        window_width, window_height = 800, 600
        
        # window_x = ((1920-window_width) // 2) + 1920
        # window_y = (1080 - window_height) //2
        # manager.window.setGeometry(window_x, window_y, window_width, window_height)
        
        # manager.window.showMaximized()
        ax2.set_xlim([0,5])
        ax2.set_ylim([0,max_amplitude])
        ax2.axis('off')
        
        if left_target_A < right_target_A:
            left_target_A -= targetHeight
        elif right_target_A < left_target_A:
            right_target_A -= targetHeight
        
        leftRangeRectangle = Rectangle(xy=(1,0), 
                                       width=1, 
                                       height=5, 
                                       color='b', zorder = 1)
        ax2.add_patch(leftRangeRectangle)

        rightRangeRectangle = Rectangle(xy = (3,0),
                                        width=1, 
                                        height=5,
                                        color='b', zorder = 1)
        ax2.add_patch(rightRangeRectangle)

        # plot Target
        leftTargetRectangle = Rectangle(xy=(1,left_target_A), 
                                        width=1, 
                                        height=targetHeight,
                                        color='orange', alpha=1.0, zorder=2)
        ax2.add_patch(leftTargetRectangle)

        rightTargetRectangle = Rectangle(xy=(3,right_target_A),
                                         width=1,
                                         height=targetHeight, 
                                         color='orange', alpha=1.0, zorder=2)
        ax2.add_patch(rightTargetRectangle)
        
        # # plot rectangle with range of the max amplitude
        # ax2.plot([1, 1], [0, max_amplitude], lw=30, c='b')
        # ax2.plot([4, 4], [0, max_amplitude], lw=30, c='b')
        
        # # plot target rectangle with an error window of 0.3
        # ax2.plot([1, 1], [left_target_A-targetWidth, left_target_A+targetWidth], lw=30, c='orange')
        # ax2.plot([4, 4], [right_target_A-targetWidth, right_target_A+targetWidth], lw=30, c='orange')
        
        # plots for current amplitude
        ax2.plot([],[],lw=5, c='red')
        ax2.plot([],[],lw=5, c='red')
        
        # Create lists for data collection
        framenumber = 0
        
        potData1 = []
        diffData1 = []
        peaks1 = []
        amplitudes1 = []
        
        potData2 = []
        diffData2 = []
        peaks2 = []
        amplitudes2 = []
        
        frames = []
        
        # create Temporary variables
        posPositiveSlope1 = 0
        posNegativeSlope1 = 0
        
        posPositivePeak1 = 0
        posNegativePeak1 = 0
        
        posPositiveSlope2 = 0
        posNegativeSlope2 = 0
        
        posPositivePeak2 = 0
        posNegativePeak2 = 0
        
        # Setup
        frames.append(framenumber)
        
        e.set()
        play_sound(self.metronomeFile)
        timeStart = time.time()
        # data visualisation loop
        while plt.fignum_exists(fig1.number) and e.is_set():

            try:
                potData1.append(self.dataPot1[-1])
                potData2.append(self.dataPot2[-1])
                diffData1.append(findTreshold(potData1[-1], potData1[-2], treshold))
                diffData2.append(findTreshold(potData2[-1], potData2[-2], treshold))
            except IndexError:
                print("waiting for data.....")
                time.sleep(1)
                timeStart = time.time()
                continue
            
            framenumber += 1
            frames.append(framenumber)
            
            # find peaks potmeter 1
            if posPositiveSlope1 & posNegativeSlope1:
                peaks1.append(int((posPositiveSlope1 + posNegativeSlope1)/2))
                if posPositiveSlope1 > posNegativeSlope1:
                    posPositivePeak1 = peaks1[-1]
                    posNegativeSlope1 = 0
                elif posPositiveSlope1 < posNegativeSlope1:
                    posNegativePeak1 = peaks1[-1]
                    posPositiveSlope1 = 0
            
            if diffData1[-1] == 1:
                posPositiveSlope1 = framenumber
            elif diffData1[-1] == -1:
                posNegativeSlope1 = framenumber
            
            # calculate amplitude potmeter 1
            
            if posPositivePeak1 & posNegativePeak1:
                amplitudes1.append(abs(potData1[posPositivePeak1] - potData1[posNegativePeak1])/29.58*50.88)
                posPositivePeak1 = 0
                posNegativePeak1 = 0
                ax2.lines[0].set_xdata([2.8, 4.2])
                ax2.lines[0].set_ydata([amplitudes1[-1], amplitudes1[-1]])
            
            # find peaks potmeter 2
            if posPositiveSlope2 & posNegativeSlope2:
                peaks2.append(int((posPositiveSlope2 + posNegativeSlope2)/2))
                if posPositiveSlope2 > posNegativeSlope2: # peak is Negative
                    posPositivePeak2 = peaks2[-1]
                    posNegativeSlope2 = 0
                elif posPositiveSlope2 < posNegativeSlope2: # peak is positive
                    posPositiveSlope2 = 0
                    posNegativePeak2 = peaks2[-1]
            
            if diffData2[-1] == 1:
                posPositiveSlope2 = framenumber
            elif diffData2[-1] == -1:
                posNegativeSlope2 = framenumber
                
            # calculate amplitude potmeter 2
            
            if posPositivePeak2 & posNegativePeak2:
                amplitudes2.append(abs(potData2[posPositivePeak2] - potData2[posNegativePeak2]))
                posPositivePeak2 = 0
                posNegativePeak2 = 0
                ax2.lines[1].set_xdata([0.8, 2.2])
                ax2.lines[1].set_ydata([amplitudes2[-1], amplitudes2[-1]])
            
            # Update plot
            ax1.lines[0].set_ydata(potData1)
            ax1.lines[0].set_xdata(frames)
            
            ax1.lines[1].set_xdata(peaks1)
            ax1.lines[1].set_ydata([potData1[i] for i in peaks1])
            
            ax1.lines[2].set_ydata(potData2)
            ax1.lines[2].set_xdata(frames)
            
            ax1.lines[3].set_xdata(peaks2)
            ax1.lines[3].set_ydata([potData2[i] for i in peaks2])
            
            if len(frames) >= 50:
                ax1.set_xlim((len(frames)-50, len(frames)+50))
            
            fig1.canvas.draw_idle()
            fig1.canvas.draw_idle()
            
            # makes sure that both figures are responsive
            fig1.canvas.flush_events()
            fig2.canvas.flush_events()
            
            # print(round(time.time()-self.timeStart,2))
            plt.pause(0.05)
        
        e.clear() # set event to false       
        aquisitionTime = time.time() - timeStart
        print('Visualisation time = ' + str(aquisitionTime))
        print("visualisation fs = {} frames/s".format(round(len(frames)/aquisitionTime,2)))
        
        plt.close('all')
        plt.figure(2)
        
        plt.plot(potData1, 'b-')
        
        for i,val in enumerate(peaks1):
            plt.plot(val, potData1[val], 'ko')
            
        plt.plot(potData2, 'r-')
        
        for i,val in enumerate(peaks2):
            plt.plot(val, potData2[val], 'ko')
            
    def startMeasuring(self):
        
        # checking if everything is ready before measuring
        # self.check_system_ready()
        
        # transform degree into voltage
        self.leftTargetVol = \
                (self.leftTargetDeg - self.calibrationFormulaPot1[1]) \
                / self.calibrationFormulaPot1[0]
        
        self.rightTargetVol = \
                (self.rightTargetDeg - self.calibrationFormulaPot2[1]) \
                / self.calibrationFormulaPot2[0]
        
        # start measuring
        measuringEvent = threading.Event()

        # start sampling in the background
        acquisitionThread = threading.Thread(target=self.data_acquisition, 
                                              daemon=True,
                                              args=(self.sampleFrequency, 
                                                    self.duration, measuringEvent)) 

        acquisitionThread.start()

        # start plotting
        self.data_visualisation(self.leftTargetVol, self.rightTargetVol, measuringEvent)
        sd.stop() # stops playing sound
        acquisitionThread.join()
        
        self.saveAsJson()
    
    
        
    
    def saveAsJson(self):
        
        os.makedirs(self.participantName, exist_ok=True)
        print(f"{self.participantName} directory is ready.")
        
        dictData = {
                'dataPot1': list(self.dataPot1),
                'dataPot2': list(self.dataPot2),
                'duration': self.duration,
                'leftTarget': self.leftTargetDeg,
                'rightTarget': self.rightTargetDeg,
                'sampleFrequency': self.sampleFrequency,
                'ZeroPointPotmeter0': self.pot0ZeroPoint,
                'ZeroPointPotmeter1': self.pot1ZeroPoint,
                'currentDate': time.strftime("%d-%m-%Y", time.localtime()),
                'currentTime': time.strftime("%H:%M:%S", time.localtime())
            }
        
        jsonData = json.dumps(dictData)
        fullFilename = f"{self.participantName}/trial_{str(self.trialNr)}.json"
        with open(fullFilename, "w") as outfile:
            outfile.write(jsonData)

        self.trialNr += 1

    
    def calcPointZero(self):
        ai_channels = ["Dev1/ai0", "Dev1/ai1"]
        
        with nidaqmx.Task() as task: 
            # Configure the AI channel
            task.ai_channels.add_ai_voltage_chan(ai_channels[0], terminal_config= TerminalConfiguration.RSE)
            task.ai_channels.add_ai_voltage_chan(ai_channels[1], terminal_config= TerminalConfiguration.RSE)
            InputData = input("Calculating zero point: Set 'elbowrest 0' to 0 degrees and press Enter...")
            self.pot0ZeroPoint = task.read()[0]
            InputData = input("Calculating zero point: Set 'elbowrest 1' to 0 degrees and press Enter...")
            self.pot1ZeroPoint = task.read()[1]
        
        # calculate regression formula as tuple --> (slope, intercept)
        self.calibrationFormulaPot1, self.calibrationFormulaPot2 = \
            calc_linear_regression(self.pot0ZeroPoint, self.pot1ZeroPoint)
            
    
    def check_system_ready(self):
        """
        This function checks if the measuring setup is ready to measure.
        The following things are checked:
            - if the nidaqmx device is connected
            - if the calibrationfiles are available in the right folder
            - if the zero point is measured
        """
        check_nidaqmx_connected()
        check_callibration_available()
        
        if not (self.pot0ZeroPoint and self.pot1ZeroPoint):

            raise ValueError("Zero point(s) of potentiometer not found. "  
                             "Use the .calcPointZero() method to set the zero points of the potentiometers!")
        
    
    
    
    
    
    