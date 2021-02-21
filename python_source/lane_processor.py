import numpy as np
import cv2

class FormerLanes:
    def __init__(self):
        self._left = []
        self._right = []
        self._leftCurvature = []
        self._rightCurvature = []
        self._offset = []

    def getLeft(self):
        return self._left[-1]

    def getRight(self):
        return self._right[-1]

    def getLeftCurvature(self):
        return self._leftCurvature[-1]

    def getRightCurvature(self):
        return self._rightCurvature[-1]

    def getOffset(self):
        return self._offset[-1]

    def newLeft(self, left):
        self._left.append(left)
        return

    def newRight(self, right):
        self._right.append(right)
        return

    def newLeftCurvature(self, leftCurvature):
        self._leftCurvature.append(leftCurvature)
        return

    def newRightCurvature(self, rightCurvature):
        self._rightCurvature.append(rightCurvature)
        return

    def newOffset(self, offset):
        self._offset.append(offset)
        return

class LaneProcessor:
    def __init__(self, binaryImage):
        """Creates a lane processor object regarding one binary image
        """
        self._nWindows = 9
        self._margin = 75
        self._minNumberOfPixels = 50
        self._originalBinaryImage = binaryImage
        self._binaryImage = binaryImage[:, :, 0]
        self._imageWidth = binaryImage.shape[1]
        self._imageHeight = binaryImage.shape[0]
        self._leftPlotX = None
        self._leftPlotY = None
        self._rightPlotX = None
        self._rightPlotY = None
        self._leftCurvatureRadian = None
        self._rightCurvatureRadian = None

    def getLeftPlotX(self):
        return self._leftPlotX

    def getRightPlotX(self):
        return self._rightPlotX

    def sanityCheck(self):
        maxDistanceOfTwoLanes = np.mean((self._rightPlotX - self._leftPlotX) * 3.7 / 640)
        if 3.4 > maxDistanceOfTwoLanes or maxDistanceOfTwoLanes > 4.0:
            return False
        if self._leftCurvatureRadian < 1000 and self._rightCurvatureRadian < 1000:
            ratio = self._rightCurvatureRadian / self._leftCurvatureRadian
            if ratio < 0.5 or ratio > 2:
                return False
        return True

    def getLeftCurvatureRadian(self):
        """Getter for left curvature radian"""
        return self._leftCurvatureRadian

    def getRightCurvatureRadian(self):
        """Getter for right curvature radian"""
        return self._rightCurvatureRadian

    def getXOffset(self):
        """Calculates the offset of the car in the lane"""
        middleOfTheLane = (self._leftPlotX[-1] + self._rightPlotX[-1]) / 2
        currentXPositions = self._imageWidth / 2
        diffInMeters = (currentXPositions - middleOfTheLane) * 3.7 / 640
        return diffInMeters

    def drawLanes(self):
        """Draws lanes which were previously generated by genarateLanePixels method"""
        image = np.zeros_like(self._originalBinaryImage).astype(np.uint8)
        leftPoints = np.array([np.transpose(np.vstack([self._leftPlotX, self._leftPlotY]))])
        rightPoints = np.array([np.flipud(np.transpose(np.vstack([self._rightPlotX, self._rightPlotY])))])
        points = np.hstack((leftPoints, rightPoints))
        return cv2.fillPoly(image, np.int_([points]), (0, 255, 0))

    def drawLanesWith(self, leftPlotX, rightPlotX):
        """Draws lanes with the parameters as lane x coordinates"""
        image = np.zeros_like(self._originalBinaryImage).astype(np.uint8)
        plotY = np.linspace(0, self._imageHeight - 1, self._imageHeight)
        leftPoints = np.array([np.transpose(np.vstack([leftPlotX, plotY]))])
        rightPoints = np.array([np.flipud(np.transpose(np.vstack([rightPlotX, plotY])))])
        points = np.hstack((leftPoints, rightPoints))
        return cv2.fillPoly(image, np.int_([points]), (255, 0, 0))

    def generateLanePixels(self):
        """Generates the lane pixels and curvature values"""
        histogram = self._histogramOfLowerPart()
        leftBaseX = self._baseLeftX(histogram)
        rightBaseX = self._baseRightX(histogram)
        nonZeros = self._nonZeroPixels()
        leftX, leftY = self._findLanePixelsOfOneLane(nonZeros, leftBaseX)
        rightX, rightY = self._findLanePixelsOfOneLane(nonZeros, rightBaseX)
        leftFitPolynomial = np.polyfit(leftY, leftX, 2)
        rightFitPolynomial = np.polyfit(rightY, rightX, 2)
        self._leftPlotX, self._leftPlotY = self._pixelsForPlotting(leftFitPolynomial)
        self._rightPlotX, self._rightPlotY = self._pixelsForPlotting(rightFitPolynomial)
        self._leftCurvatureRadian = self._calculateCurvature(leftX, leftY)
        self._rightCurvatureRadian = self._calculateCurvature(rightX, rightY)
        return

    def _histogramOfLowerPart(self):
        """Creates the histogram of the lower part of the image"""
        return np.sum(self._binaryImage[self._imageHeight // 2:, :], 0)

    def _baseLeftX(self, histogram):
        """Results the histogram peak on the left hand side"""
        return np.argmax(histogram[:self._imageWidth // 2])

    def _baseRightX(self, histogram):
        """Results the histogram peak on the right hand side"""
        middlePoint = self._imageWidth // 2
        return np.argmax(histogram[middlePoint:]) + middlePoint

    def _nonZeroPixels(self):
        """Results all nonzero pixels of the image"""
        nonZeros = self._binaryImage.nonzero()
        return np.array(nonZeros[1]), np.array(nonZeros[0]) # x and y coordinates of nonzeros

    def _findLanePixelsOfOneLane(self, nonzeros, baseXCoordinate):
        """Find the lane pixels using windowing technique"""
        windowHeight = np.int(self._imageHeight / self._nWindows)
        nonZeroPixelsYCoors = nonzeros[1]
        nonZeroPixelsXCoors = nonzeros[0]

        currentXCoordinate = baseXCoordinate
        laneIndices = []
        for window in range(self._nWindows):
            lowYInWindow = self._imageHeight - (window + 1) * windowHeight
            highYInWindow = self._imageHeight - window * windowHeight
            lowXInWindow = currentXCoordinate - self._margin
            highXInWindow = currentXCoordinate + self._margin

            goodIndices = ((lowYInWindow <= nonZeroPixelsYCoors) & (nonZeroPixelsYCoors < highYInWindow) & (lowXInWindow <= nonZeroPixelsXCoors) & (nonZeroPixelsXCoors < highXInWindow)).nonzero()[0]
            laneIndices.append(goodIndices)
            if len(goodIndices) > self._minNumberOfPixels:
                currentXCoordinate = np.int(np.mean(nonZeroPixelsXCoors[goodIndices]))

        try: 
            laneIndices = np.concatenate(laneIndices)
        except ValueError:
            pass

        finalXCoordinates = nonZeroPixelsXCoors[laneIndices]
        finalYCoordinates = nonZeroPixelsYCoors[laneIndices]
        return finalXCoordinates, finalYCoordinates

    def _pixelsForPlotting(self, fittingPolynomial):
        """Generates pixels for plotting a lane"""
        yValues = np.linspace(0, self._imageHeight - 1, self._imageHeight)
        try:
            fittingXCoordinates = fittingPolynomial[0] * yValues**2 + fittingPolynomial[1] * yValues + fittingPolynomial[2]
        except TypeError:
            fittingXCoordinates = yValues**2 + yValues
        return fittingXCoordinates, yValues

    def _calculateCurvature(self, xCoordinates, yCoordinates):
        """Calculates the curvature of a lane"""
        yMetersPerPixel = 35 / self._imageHeight
        xMetersPerPixel = 3.7 / 640
        fittingPolynomial = np.polyfit(yCoordinates * yMetersPerPixel, xCoordinates * xMetersPerPixel, 2)
        yValues = np.linspace(0, self._imageHeight - 1, self._imageHeight)
        curveRad = ((1 + (2 * fittingPolynomial[0] * np.max(yValues) * yMetersPerPixel + fittingPolynomial[1])**2)**1.5) / np.abs(2 * fittingPolynomial[0])
        return curveRad