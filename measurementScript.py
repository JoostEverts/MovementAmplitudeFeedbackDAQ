# measurementScript.py

# imports
from measurement_toolbox.GUI_tools import GeneralSettingsGUI, MeasurementSettingsGUI
from measurement_toolbox.measurement import MeasurementDAQ
from measurement_toolbox.utils import check_nidaqmx_connected, check_callibration_available

# %% Checks

# check nidaqmx device connected
check_nidaqmx_connected()

# Check if calibration files are available
check_callibration_available()

# %% Start measuring program

generalSettings = GeneralSettingsGUI()
experiment = MeasurementDAQ(generalSettings.settings)

while True:

    measurementSettings = MeasurementSettingsGUI(experiment.trialNr,
                                                 generalSettings.settings["useExcel"],
                                                 generalSettings.excelSettings)

    experiment.startMeasuring(measurementSettings.settings)
