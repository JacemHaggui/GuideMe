import numpy as np
import cv2 as cv

# HSV settings for lower red (around 0-10 in hue)
hueLow1 = 0         # Lower bound for hue (start of red range)
hueHigh1 = 10       # Upper bound for hue (end of lower red range)
satLow = 150        # Lower bound for saturation
satHigh = 255       # Upper bound for saturation
valLow = 80        # Lower bound for value (brightness)
valHigh = 255       # Upper bound for value (brightness)

lowerBound1 = np.array([hueLow1, satLow, valLow])
upperBound1 = np.array([hueHigh1, satHigh, valHigh])

# HSV settings for upper red (around 170-179 in hue)
hueLow2 = 170       # Lower bound for hue (start of upper red range)
hueHigh2 = 179      # Upper bound for hue (end of red range)
lowerBound2 = np.array([hueLow2, satLow, valLow])
upperBound2 = np.array([hueHigh2, satHigh, valHigh])

# HSV settings for feet detection (blue color detection)
hueLow = 80   # Lower bound for Hue (Blue starts around 100 in HSV)
hueHigh = 140  # Upper bound for Hue (Blue ends around 140 in HSV)
satLow = 100  # Lower bound for Saturation
satHigh = 255 # Upper bound for Saturation
valLow = 100  # Lower bound for Value (brightness)
valHigh = 255 # Upper bound for Value (brightness)

# Create the lower and upper bounds for the yellow color
lowerBoundYellow = np.array([hueLow, satLow, valLow])
upperBoundYellow = np.array([hueHigh, satHigh, valHigh])

# Function to create HSV masks
def create_hsv_mask(frame, lowerBound, upperBound):
    frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(frameHSV, lowerBound, upperBound)
    return mask

def median_filter(mask, kernel_size=3):
    return cv.medianBlur(mask, kernel_size)