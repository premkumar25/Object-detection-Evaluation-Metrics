from pathlib import Path
import os
import sys
import shutil
import _init_paths
from utils import BBFormat, CoordinatesType
import numpy as np


# Get current path to set default folders
currentPath = os.path.dirname(os.path.abspath(__file__))

# Get folder details
gtFolder = Path(os.path.join(currentPath, 'groundtruths'))
detFolder = Path(os.path.join(currentPath, 'detections_1'))
savePath = Path(os.path.join(currentPath, 'results'))

# Confidence threshold values (starting value, end value, step change) - Change as per your requirement
conf_threshold = np.arange(0.1, 1.0, 0.05)

# IOU threshold values - Change as per your requirement
iouThreshold = [0.5, 0.6]

# Validate formats
def ValidateFormats(argFormat, argName):
    if argFormat == 'xywh':
        return BBFormat.XYWH
    elif argFormat == 'xyrb':
        return BBFormat.XYX2Y2
    elif argFormat is None:
        return BBFormat.XYWH  # default when nothing is passed
    else:
        return ('argument %s: invalid value. It must be either \'xywh\' or \'xyrb\'' %
                      argName)


# Validate coordinate types
def ValidateCoordinatesTypes(arg, argName):
    if arg == 'abs':
        return CoordinatesType.Absolute
    elif arg == 'rel':
        return CoordinatesType.Relative
    elif arg is None:
        return CoordinatesType.Absolute  # default when nothing is passed
    else:
        return ('argument %s: invalid value. It must be either \'rel\' or \'abs\'' % argName)


# Check if path to save results already exists and is not empty
if os.path.isdir(savePath) and os.listdir(savePath):
    key_pressed = ''
    while key_pressed.upper() not in ['Y', 'N']:
        print(f'Folder {savePath} already exists and may contain important results.\n')
        print(f'Enter \'Y\' to continue. WARNING: THIS WILL REMOVE ALL THE CONTENTS OF THE FOLDER!')
        print(f'Or enter \'N\' to abort and choose another folder to save the results.')
        key_pressed = input('')

    if key_pressed.upper() == 'N':
        print('Process canceled')
        sys.exit()

# Clear folder and save results
shutil.rmtree(savePath, ignore_errors=True)
os.makedirs(savePath)

# Get the optional formats
## Default format is 'xyrb' you can also use 'xywh'
gtFormat = ValidateFormats('xyrb', '-gtformat')
detFormat = ValidateFormats('xyrb', '-detformat')
# Coordinates types
gtCoordType = ValidateCoordinatesTypes('abs', '-gtCoordinates')
detCoordType = ValidateCoordinatesTypes('abs', '-detCoordinates')

# Default for coordinate type 'abs' if coordinate type is 'rel' change the image size according to your requirement
imgSize = (0, 0)
