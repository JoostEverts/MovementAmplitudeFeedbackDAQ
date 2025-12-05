# example_usage.py
from potmeter_experiment.measurement import PotmeterMeasurement


#%% pruts
left_target_amplitude = 30
right_target_amplitude = 30
sampleFrequency = 300
duration = 30
metronomeDuration = 15 # duration of metronome after starting the measurement
metronomeFile = "Metronome15Hz.wav"
potClass = PotmeterMeasurement("pruts", left_target_amplitude,
                               right_target_amplitude, sampleFrequency,
                               duration, metronomeFile, metronomeDuration)
# variabelen:
    
# potClass.duration
# potClass.trialNr
# potClass.leftTarget
# potClass.rightTarget

potClass.pot0ZeroPoint = 1   
potClass.pot1ZeroPoint = 1

# functies:


# potClass.calcPointZero()    
# potClass.startMeasuring()
#%% pruts

#data1, data2 = calc_linear_regression()