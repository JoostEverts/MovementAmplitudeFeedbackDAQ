# GUI_tools.py

# %% imports
import tkinter as tk
import json
import sys
from .utils import read_json, get_excel_settings
from .calibration import calc_intercept

# %% Create a class for a base GUI


class BaseGUI:

    def __init__(self):

        self.entries = {}

        try:
            self.settings = read_json(
                "calibration_files/previousSettings.json")

        except FileNotFoundError:
            self.settings = {}

        self.root = tk.Tk()
        self.root.grid_columnconfigure(2, minsize=150)
        self.root.geometry("800x800")  # size

    def create_labeled_entry(self, row, column, key, message):

        # is used for the generic labels and texbox settings

        label = tk.Label(self.root, text=message, font=("Arial", 10))
        label.grid(column=column, row=row, padx=10, pady=10)

        textbox = tk.Entry(self.root, width=20, font=("Arial", 10))
        textbox.grid(column=column+1, row=row, padx=10, pady=10)

        if key in self.settings:
            textbox.insert(0, str(self.settings[key]))

        self.entries[key] = textbox

    def collect_settings(self):
        # get_gettings runs when 'Start measuring' button is pressed
        for key, value in self.entries.items():
            self.settings[key] = value.get().strip()

    def save_settings(self):

        with open("calibration_files/previousSettings.json", "w") as f:
            json.dump(self.settings, f)

    def on_close(self):
        print("Window closed. Exiting program.")
        self.root.destroy()
        sys.exit(0)

# %% General Settings GUI


class GeneralSettingsGUI(BaseGUI):

    def __init__(self):

        super().__init__()
        self.root.title("General Settings GUI")  # title

        # General settings
        settingsTitle = tk.Label(
            self.root, text="General Settings", font=("Helvetica", 14))
        settingsTitle.grid(column=0, row=0, padx=10, pady=10, columnspan=2)
        self.create_labeled_entry(1, 0, "participantName", "Name Participant")
        self.create_labeled_entry(2, 0, "sampleFrequency", "Sample Frequency")

        # checkbox excel file
        self.stateCheckExcel = tk.IntVar()
        self.checkExcel = tk.Checkbutton(self.root, text="Run experiment with excel file",
                                         font=("Arial", 10), variable=self.stateCheckExcel)
        self.checkExcel.grid(column=0, row=3, padx=10, pady=10, columnspan=2)

        # Feedback settings
        settingsTitle = tk.Label(
            self.root, text="Feedback Settings", font=("Helvetica", 14))
        settingsTitle.grid(column=0, row=4, padx=10, pady=10, columnspan=2)
        self.create_labeled_entry(
            5, 0, "minFeedback", "Minimum Feedback Amplitude")
        self.create_labeled_entry(
            6, 0, "maxFeedback", "Maximum Feedback Amplitude")
        self.create_labeled_entry(
            7, 0, "targetBarHeight", "Target Amplitude Height")
        self.create_labeled_entry(
            8, 0, "feedbackBarHeight", "Feedback Bar Height")

        # calculate calibration offset
        interceptTitle = tk.Label(
            self.root, text="Calculate Calibration Offset", font=("Helvetica", 14))
        interceptTitle.grid(column=0, row=9, padx=10, pady=10, columnspan=2)

        # Labels offset calculations
        offsetInputValueLabel = tk.Label(
            self.root, text="Input Value", font=("Helvetica", 10))
        offsetInputValueLabel.grid(column=0, row=10, padx=10, pady=10)

        offsetOutputValueLabel = tk.Label(
            self.root, text="Output Value [Voltage]", font=("Helvetica", 10))
        offsetOutputValueLabel.grid(column=2, row=10, padx=10, pady=10)

        # Channel 0 offset
        self.channel0Input = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.channel0Input.grid(column=0, row=11, padx=10, pady=10)

        self.channel0InterceptButton = tk.Button(self.root, text="Calculate Offset Channel 0",
                                                 command=lambda: self.set_point_zero(
                                                     0),
                                                 font=("Helvetica", 10))
        self.channel0InterceptButton.grid(column=1, row=11, padx=10, pady=10)

        self.channel0Entry = tk.Entry(
            self.root, width=20, font=("Arial", 10), state=tk.DISABLED)
        self.channel0Entry.grid(column=2, row=11, padx=10, pady=10)

        # Channel 1 offset

        self.channel1Input = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.channel1Input.grid(column=0, row=12, padx=10, pady=10)

        self.channel1InterceptButton = tk.Button(self.root, text="Calculate Offset Channel 1",
                                                 command=lambda: self.set_point_zero(
                                                     1),
                                                 font=("Helvetica", 10))
        self.channel1InterceptButton.grid(column=1, row=12, padx=10, pady=10)

        self.channel1Entry = tk.Entry(
            self.root, width=20, font=("Arial", 10), state=tk.DISABLED)
        self.channel1Entry.grid(column=2, row=12, padx=10, pady=10)

        # submit button

        self.submitButton = tk.Button(
            self.root, text="Submit", command=self.submit_settings, font=("Helvetica", 10))
        self.submitButton.grid(column=1, row=13, padx=10,
                               pady=10, columnspan=1)

        # when window is closed stop script
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # activate GUI
        self.root.mainloop()

    def set_point_zero(self, channelnr):

        # calculates the intercept of a given channelnr and displays it in the GUI
        if channelnr == 0:
            inputValue = float(self.channel0Input.get())

        elif channelnr == 1:
            inputValue = float(self.channel1Input.get())

        intercept = calc_intercept(channelnr, inputValue)
        key = "interceptAI" + str(channelnr)
        self.settings[key] = intercept

        if channelnr == 0:
            self.channel0Entry.config(state=tk.NORMAL)
            self.channel0Entry.delete(0, tk.END)
            self.channel0Entry.insert(0, str(intercept[1]))
            self.channel0Entry.config(state=tk.DISABLED)

        elif channelnr == 1:
            self.channel1Entry.config(state=tk.NORMAL)
            self.channel1Entry.delete(0, tk.END)
            self.channel1Entry.insert(0, str(intercept[1]))
            self.channel1Entry.config(state=tk.DISABLED)

    def submit_settings(self):
        self.collect_settings()
        self.settings["useExcel"] = self.stateCheckExcel.get()

        # check settings
        try:
            self.settings["sampleFrequency"] = int(
                self.settings["sampleFrequency"])
            self.settings["minFeedback"] = float(self.settings["minFeedback"])
            self.settings["maxFeedback"] = float(self.settings["maxFeedback"])
            self.settings["targetBarHeight"] = float(
                self.settings["targetBarHeight"])
            self.settings["feedbackBarHeight"] = float(
                self.settings["feedbackBarHeight"])
            # save and destroy
            self.root.destroy()
            self.save_settings()

        except ValueError:
            print("Invalid numeric input")
            invalidLabel = tk.Label(
                self.root, text="Invalid numeric inputs", fg='red')
            invalidLabel.grid(column=2, row=12, padx=10, pady=10)

        if self.settings["useExcel"] == 1:
            self.excelSettings = get_excel_settings()
        else:
            self.excelSettings = {}


# %% Measurement Settings GUI

class MeasurementSettingsGUI(BaseGUI):

    def __init__(self, trialNumber, use_excel, excel_settings={}):
        super().__init__()
        self.root.title(" Measurement Settings GUI")  # title

        self.trialNr = trialNumber
        self.useExcel = use_excel
        self.excelSettings = excel_settings

        if (self.useExcel == 1) and (self.trialNr <= len(self.excelSettings)):
            self.update_settings_with_excel()

        # main title
        mainTitle = tk.Label(
            self.root, text="Measurement Settings", font=("Helvetica", 16))
        mainTitle.grid(column=0, row=0, padx=10, pady=10, columnspan=2)

        # trial number entry

        self.trialLabel = tk.Label(self.root,
                                   text="Trial Number",
                                   font=("Arial", 10))
        self.trialLabel.grid(column=0, row=1, padx=10, pady=10)

        self.trialEntry = tk.Entry(self.root,
                                   width=20,
                                   font=("Arial", 10))
        self.trialEntry.grid(column=1, row=1, padx=10, pady=10)
        self.trialEntry.insert(0, str(self.trialNr))

        self.trialChangeButton = tk.Button(self.root,
                                           text="Change Trial Number",
                                           command=self.on_trial_change,
                                           font=("Helvetica", 10))
        self.trialChangeButton.grid(column=2, row=1, padx=10, pady=10)

        # settings title
        self.settingsTitle = tk.Label(self.root, text=f"Settings Trial {
                                      self.trialNr}:", font=("Helvetica", 12))
        self.settingsTitle.grid(
            column=0, row=2, padx=10, pady=10, columnspan=2)

        # measurement settings entries

        self.create_labeled_entry(
            4, 0, "rightTarget", "Right Target Amplitude")
        self.create_labeled_entry(5, 0, "leftTarget", "Left Target Amplitude")
        self.create_labeled_entry(6, 0, "duration", "Trial Duration [s]")
        self.create_labeled_entry(
            7, 0, "metronomeDuration", "Metronome Duration [s]")
        self.create_labeled_entry(8, 0, "metronomeFile", "Metronome filename")

        if (self.useExcel == 1) and (self.trialNr <= len(self.excelSettings)):
            self.disable_entries()

        # start measuring button
        self.submitButton = tk.Button(
            self.root, text="Start Measurement", command=self.get_settings, font=("Helvetica", 10))
        self.submitButton.grid(column=1, row=10, padx=10,
                               pady=10, columnspan=1)

        # when window is closed stop script
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.mainloop()

    def on_trial_change(self):
        self.trialNr = int(self.trialEntry.get())
        self.settingsTitle.config(text=f"Settings Trial {self.trialNr}:")

        if (self.useExcel == 1) and (self.trialNr <= len(self.excelSettings)):
            self.update_settings_with_excel()
            self.enable_entries()
            for key, value in self.entries.items():
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, str(self.settings[key]))
            self.disable_entries()
        elif (self.useExcel == 1) and (self.trialNr > len(self.excelSettings)):
            self.enable_entries()

    def disable_entries(self):
        for key, value in self.entries.items():
            self.entries[key].config(state=tk.DISABLED)

    def enable_entries(self):
        for key, value in self.entries.items():
            self.entries[key].config(state=tk.NORMAL)

    def update_settings_with_excel(self):
        excelIndex = self.trialNr - 1
        self.settings["rightTarget"] = float(
            self.excelSettings.loc[excelIndex, "Target_Right_Limb"])
        self.settings["leftTarget"] = float(
            self.excelSettings.loc[excelIndex, "Target_Left_Limb"])
        self.settings["duration"] = float(
            self.excelSettings.loc[excelIndex, "Trial_Duration"])
        self.settings["metronomeDuration"] = float(
            self.excelSettings.loc[excelIndex, "Metronome_Duration"])
        self.settings["metronomeFile"] = str(
            self.excelSettings.loc[excelIndex, "Metronome_Filename"])

    def get_settings(self):

        # get_gettings runs when 'Start measuring' button is pressed
        self.collect_settings()
        self.settings['trialNr'] = self.trialEntry.get().strip()

        # Check if settings have the correct datatype
        try:
            self.settings["rightTarget"] = float(self.settings["rightTarget"])
            self.settings["leftTarget"] = float(self.settings["leftTarget"])

            self.settings["duration"] = float(self.settings["duration"])
            self.settings["metronomeDuration"] = float(
                self.settings["metronomeDuration"])
            self.settings["trialNr"] = int(self.settings["trialNr"])
            self.root.destroy()
            self.save_settings()

        except ValueError:
            print("Invalid numeric input")
            invalidLabel = tk.Label(
                self.root, text="Invalid numeric inputs", fg='red')
            invalidLabel.grid(column=2, row=10, padx=10, pady=10)
