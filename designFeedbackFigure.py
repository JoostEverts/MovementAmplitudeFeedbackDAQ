# designFeedbackFigure.py

# %% Imports
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# %% Design Feedback Figure by changing parameters


# left and right target amplitude from measurement GUI
leftTargetAmplitude = 2
rightTargetAmplitude = 3

# feedback figure settings from General GUI

minAmplitude = 0  # Minimum Feedback Amplitude
maxAmplitude = 5  # Maximum Feedback Amplitude
targetSize = 0.5  # Target Amplitude Height
feedbackBarSize = 5  # Feedback Bar Height

# %% data visualisation function


def data_visualisation(left_target_A, right_target_A, maxAmplitude,
                       minAmplitude, targetSize, feedbackBarSize):

    # makes sure the middle of the target = the given target amplitude
    left_target_A = left_target_A - (targetSize/2)
    right_target_A = right_target_A - (targetSize/2)

    # setup Potentiometer data plot
    plt.close('all')
    plt.ion()

    # Setup online feedback plot
    fig2, ax2 = plt.subplots()

    # manager.window.showMaximized()
    ax2.set_xlim([0, 5])
    ax2.set_ylim([minAmplitude, maxAmplitude])
    # ax2.axis('off')
    ax2.grid()

    # plot blue range bars
    leftRangeRectangle = Rectangle(xy=(1, 0),
                                   width=1,
                                   height=maxAmplitude,
                                   color='b', zorder=1)
    ax2.add_patch(leftRangeRectangle)

    rightRangeRectangle = Rectangle(xy=(3, 0),
                                    width=1,
                                    height=maxAmplitude,
                                    color='b', zorder=1)
    ax2.add_patch(rightRangeRectangle)

    # plot Target
    leftTargetRectangle = Rectangle(xy=(1, left_target_A),
                                    width=1,
                                    height=targetSize,
                                    color='orange', alpha=1.0, zorder=2)
    ax2.add_patch(leftTargetRectangle)

    rightTargetRectangle = Rectangle(xy=(3, right_target_A),
                                     width=1,
                                     height=targetSize,
                                     color='orange', alpha=1.0, zorder=2)
    ax2.add_patch(rightTargetRectangle)

    # plots for current amplitude
    ax2.plot([], [], lw=feedbackBarSize, c='red')
    ax2.plot([], [], lw=feedbackBarSize, c='red')

    ax2.lines[0].set_xdata([2.8, 4.2])
    ax2.lines[0].set_ydata([right_target_A, right_target_A])

    ax2.lines[1].set_xdata([0.8, 2.2])
    ax2.lines[1].set_ydata([left_target_A, left_target_A])


# %% Plot feedback Figure
data_visualisation(leftTargetAmplitude, rightTargetAmplitude,
                   maxAmplitude, minAmplitude,
                   targetSize, feedbackBarSize)
