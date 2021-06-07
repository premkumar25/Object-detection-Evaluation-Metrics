# import pascalvoc
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from pathlib import Path

import _init_paths
import settings
from BoundingBox import BoundingBox
from BoundingBoxes import BoundingBoxes
from Evaluator import *
from utils import BBFormat


def getBoundingBoxes(directory,
                     isGT,
                     bbFormat,
                     coordType,
                     allBoundingBoxes=None,
                     allClasses=None,
                     imgSize=(0, 0),
                     conf_threshold=0):
    """Read txt files containing bounding boxes (ground truth and detections)."""
    if allBoundingBoxes is None:
        allBoundingBoxes = BoundingBoxes()
    if allClasses is None:
        allClasses = []
    # Read ground truths
    os.chdir(directory)
    files = glob.glob("*.txt")
    files.sort()
    # Read GT detections from txt file
    # Each line of the files in the groundtruths folder represents a ground truth bounding box
    # (bounding boxes that a detector should detect)
    # Each value of each line is  "class_id, x, y, width, height" respectively
    # Class_id represents the class of the bounding box
    # x, y represents the most top-left coordinates of the bounding box
    # x2, y2 represents the most bottom-right coordinates of the bounding box
    for f in files:
        nameOfImage = f.replace(".txt", "")
        fh1 = open(f, "r")
        for line in fh1:
            line = line.replace("\n", "")
            if line.replace(' ', '') == '':
                continue
            splitLine = line.split(" ")
            # bb = None
            if isGT and conf_threshold == 0:
                # idClass = int(splitLine[0]) #class
                idClass = (splitLine[0])  # class
                x = float(splitLine[1])
                y = float(splitLine[2])
                w = float(splitLine[3])
                h = float(splitLine[4])
                bb = BoundingBox(nameOfImage,
                                 idClass,
                                 x,
                                 y,
                                 w,
                                 h,
                                 coordType,
                                 imgSize,
                                 BBType.GroundTruth,
                                 format=bbFormat)
                allBoundingBoxes.addBoundingBox(bb)
                if idClass not in allClasses:
                    allClasses.append(idClass)
            elif float(splitLine[1]) >= round(conf_threshold, 2):
                # idClass = int(splitLine[0]) #class
                idClass = (splitLine[0])  # class
                confidence = float(splitLine[1])
                x = float(splitLine[2])
                y = float(splitLine[3])
                w = float(splitLine[4])
                h = float(splitLine[5])
                bb = BoundingBox(nameOfImage,
                                 idClass,
                                 x,
                                 y,
                                 w,
                                 h,
                                 coordType,
                                 imgSize,
                                 BBType.Detected,
                                 confidence,
                                 format=bbFormat)
            # if bb:
                allBoundingBoxes.addBoundingBox(bb)
                if idClass not in allClasses:
                    allClasses.append(idClass)
        fh1.close()
    return allBoundingBoxes, allClasses


## Get the metics result.txt file for various confidence threshold
def getMetrics(conf_threshold, iouThreshold):
    for i in conf_threshold:
        # Get groundtruth boxes
        allBoundingBoxes, allClasses = getBoundingBoxes(settings.gtFolder,
                                                        True,
                                                        settings.gtFormat,
                                                        settings.gtCoordType,
                                                        imgSize=settings.imgSize)
        os.chdir(settings.detFolder)
        files = glob.glob("*.txt")
        files.sort()
        for f in files:
            nameOfImage = f.replace(".txt", "")
            fh1 = open(f, "r")
            for line in fh1:
                line = line.replace("\n", "")
                if line.replace(' ', '') == '':
                    continue
                splitLine = line.split(" ")
                if float(splitLine[1]) >= round(i, 2):
                    # Get detected boxes
                    idClass = splitLine[0]
                    confidence = splitLine[1]
                    x = float(splitLine[2])
                    y = float(splitLine[3])
                    w = float(splitLine[4])
                    h = float(splitLine[5])
                    bb = BoundingBox(nameOfImage,
                                     idClass,
                                     x,
                                     y,
                                     w,
                                     h,
                                     settings.detCoordType,
                                     settings.imgSize,
                                     BBType.Detected,
                                     confidence,
                                     format=settings.detFormat)

                    allBoundingBoxes.addBoundingBox(bb)
                    if idClass not in allClasses:
                        allClasses.append(idClass)
            fh1.close()

        allClasses.sort()

        evaluator = Evaluator()
        acc_AP = 0
        validClasses = 0

        for iou in iouThreshold:
            # Plot Precision x Recall curve
            ## This calls evaluator.py and plots Precision x Recall curve
            ### Comment those lines in evaluator.py
            detections = evaluator.PlotPrecisionRecallCurve(
                allBoundingBoxes,  # Object containing all bounding boxes (ground truths and detections)
                IOUThreshold=iou,  # IOU threshold
                method=MethodAveragePrecision.EveryPointInterpolation,
                showAP=True,  # Show Average Precision in the title of the plot
                showInterpolatedPrecision=False,  # Don't plot the interpolated precision curve
                savePath=settings.savePath)

            f = open(os.path.join(settings.savePath, 'results_'+str(iou)+'_threshold.txt'), 'a')
            # Uncomment for precision x recall curve
            # fp = open(os.path.join(settings.savePath, 'results_PxR_'+str(iou)+'_threshold.txt'), 'w')
            # fp.write('Object Detection Metrics\n')
            # fp.write('https://github.com/rafaelpadilla/Object-Detection-Metrics\n\n\n')
            # fp.write('Average Precision (AP), Precision and Recall per class:')

            # each detection is a class
            for metricsPerClass in detections:

                # Get metric values per each class
                cl = metricsPerClass['class']
                ap = metricsPerClass['AP']
                precision = metricsPerClass['precision']
                recall = metricsPerClass['recall']
                totalPositives = metricsPerClass['total positives']
                total_TP = metricsPerClass['total TP']
                total_FP = metricsPerClass['total FP']

                validClasses = validClasses + 1
                acc_AP = acc_AP + ap
                prec = ['%.2f' % p for p in precision]
                rec = ['%.2f' % r for r in recall]
                ap_str = "{0:.2f}".format(ap)
                # ap_str = "{0:.4f}%".format(ap * 100)
                f.write('\n %s' % cl)
                f.write(' %s' % ap_str)
                f.write(' %s' % round(i, 2))
                f.write(' '+prec[-1]+' ')
                f.write(rec[-1] if rec[-1] != 'nan' else str(0))
                # fp.write('\n\nClass: %s' % cl)                  # Uncomment for precision x recall curve
                # fp.write('\nAP: %s' % ap_str)                   # Uncomment for precision x recall curve
                # fp.write('\nPrecision: %s' % prec)              # Uncomment for precision x recall curve
                # fp.write('\nRecall: %s' % rec)                  # Uncomment for precision x recall curve

            # mAP = acc_AP / validClasses                         # Uncomment for precision x recall curve
            # mAP_str = "{0:.2f}%".format(mAP * 100)              # Uncomment for precision x recall curve
            # print('mAP: %s' % mAP_str)                          # Uncomment for precision x recall curve
            # fp.write('\n\n\nmAP: %s' % mAP_str)                 # Uncomment for precision x recall curve

        classes = allClasses
        allBoundingBoxes = None
        allClasses = None
        # break
    return classes


def plot_conf_threshold(iouThreshold, classes):
    for iou in iouThreshold:
        for cls in classes:
            conf_score = []
            precision = []
            recall = []
            avg_prec = []

            with open(os.path.join(settings.savePath, 'results_'+str(iou)+'_threshold.txt')) as files:
                for line in files:
                    line = line.replace("\n", "")
                    if line.replace(' ', '') == '':
                        continue
                    splitLine = line.split(" ")
                    if splitLine[1] == cls:
                        conf_score.append(splitLine[3])
                        precision.append(float(splitLine[4]))
                        recall.append(float(splitLine[5]))
                        avg_prec.append(float(splitLine[2]))

            plt.title('Confidence threshold x (Precision, Recall, AP)\n IOU Threshold: %s Class: %s' % (iou, cls))
            plt.xlabel('confidence_threshold')
            plt.ylabel('precision x recall')
            plt.plot(conf_score, precision)
            plt.plot(conf_score, recall)
            plt.plot(conf_score, avg_prec)
            plt.legend(["precision", "recall", 'avg_precison'], loc="lower right")
            plt.savefig(os.path.join(settings.savePath, cls + '_' + str(iou)+'_thershold.png'))
            plt.show()


# Confidence threshold
conf_threshold = settings.conf_threshold

# IOU threshold
iouThreshold = settings.iouThreshold
# classes = []

## Get precision, recall, avg_precision x Confidence threshold

## Get precision, recall for various confidence threshold
classes = getMetrics(conf_threshold, iouThreshold)

## Plot precision, recall, average precision x Confidence threshold
plot_conf_threshold(iouThreshold, classes)

## Get precision x recall for diff IOU threshold
### Give confidence threshold a single value as precision x recall is calculated for
### different IOU threshold and single confidence threshold
### Note : uncomment the plt lines in Evalutator.py inorder to get precision x recall graph
### Comment the above two statements and run the following

# conf_threshold = [0.7]
# getMetrics(conf_threshold, iouThreshold)
