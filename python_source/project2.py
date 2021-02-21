import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt
import pickle
from moviepy.editor import VideoFileClip

from camera_calibration import CameraCalibration
from perspective_transform import PerspectiveTransform
from lane_processor import LaneProcessor
from lane_processor import FormerLanes
from gradients_and_color import GradientsAndColor

camera = CameraCalibration(9, 6)
perspectiveTransform = PerspectiveTransform((1280, 720))
formerLanes = FormerLanes()
def processImage(image):
    undistortedImage = camera.undistort(image)
    gradientsAndColor = GradientsAndColor(undistortedImage)
    lanePixelCandidates = gradientsAndColor.colorAndGradientFiltering()
    warpLanes = perspectiveTransform.warp(lanePixelCandidates)
    laneProcessor = LaneProcessor(warpLanes)
    laneProcessor.generateLanePixels()
    if laneProcessor.sanityCheck():
        drawnLanes = laneProcessor.drawLanes()
        formerLanes.newLeft(laneProcessor.getLeftPlotX())
        formerLanes.newRight(laneProcessor.getRightPlotX())
        leftCurvatureRadian = laneProcessor.getLeftCurvatureRadian()
        formerLanes.newLeftCurvature(leftCurvatureRadian)
        rightCurvatureRadian = laneProcessor.getRightCurvatureRadian()
        formerLanes.newRightCurvature(rightCurvatureRadian)
        xOffset = laneProcessor.getXOffset()
        formerLanes.newOffset(xOffset)
    else:
        drawnLanes = laneProcessor.drawLanesWith(formerLanes.getLeft(), formerLanes.getRight())
        leftCurvatureRadian = formerLanes.getLeftCurvature()
        rightCurvatureRadian = formerLanes.getRightCurvature()
        prevXOffset = formerLanes.getOffset()
    unWarpedLanes = perspectiveTransform.unWarp(drawnLanes)
    newImage = cv2.addWeighted(undistortedImage, 1, unWarpedLanes, 0.3, 0)
    leftCurvatureRadian = laneProcessor.getLeftCurvatureRadian()
    rightCurvatureRadian = laneProcessor.getRightCurvatureRadian()
    xOffset = laneProcessor.getXOffset()
    text1 = 'Left curvature: {0:5.0f} meters, right curvature: {1:5.0f} meters'.format(leftCurvatureRadian, rightCurvatureRadian)
    text2 = 'Horizontal car offset: {0:.2f} meters'.format(xOffset)
    newImage = cv2.putText(newImage, text1, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return cv2.putText(newImage, text2, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

inputVideo = VideoFileClip(filename = 'project_video.mp4')
outputVideoFile = 'result_project_video.mp4'
outputVideo = inputVideo.fl_image(image_func = processImage)
outputVideo.write_videofile(outputVideoFile, audio = False)

# image = cv2.imread('test_images/straight_lines1.jpg')
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# outputImage = processImage(image)
# plt.imshow(outputImage)
# plt.show()
