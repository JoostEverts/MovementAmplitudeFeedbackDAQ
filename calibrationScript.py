# calibrationScript.py

# %% imports
from measurement_toolbox.calibration import start_calibrating
from measurement_toolbox.utils import check_nidaqmx_connected


# %% Input values
# Choose which potentiometer you want to calibrate.
channel = 1  # Can either be 1 or 0

# Choose start value, stop value and increments of calibration
start = 0
stop = 5
increment = 0.5

# %% Run calibration

check_nidaqmx_connected()  # check nidaqmx device connected
start_calibrating(channel, start, stop, increment)
