import numpy as np
import cv2

class PerspectiveTransform:
    def __init__(self, imageSize):
        """Creates  perspective transform object

        imageSize - width and height of an image
        """
        self._imageSize = imageSize
        self._sourcePoints = self._createSource()
        self._destinationPoints = self._createDestination()
        self._transformationMatrix = cv2.getPerspectiveTransform(self._sourcePoints, self._destinationPoints)
        self._inverseTransformationMatrix = cv2.getPerspectiveTransform(self._destinationPoints, self._sourcePoints)
        
    def _createSource(self):
        """Creates source matrix
        
        Results source matrix representing a trapezoid
        """
        xOffsetBottom = 200
        xOffsetMiddle = 595
        yOffset = 450
        sourceBottomLeft = (xOffsetBottom, self._imageSize[1])
        sourceBottomRight = (self._imageSize[0] - xOffsetBottom, self._imageSize[1])
        sourceTopLeft = (xOffsetMiddle, yOffset)
        sourceTopRight = (self._imageSize[0] - xOffsetMiddle, yOffset)
        return np.float32([sourceBottomLeft, sourceTopLeft, sourceTopRight, sourceBottomRight])

    def _createDestination(self):
        """Creates destination matrix

        Results destination matrix representing a rectangle
        """
        xOffset = self._imageSize[0] / 4
        destinationBottomLeft = (xOffset, self._imageSize[1])
        destinationBottomRight = (self._imageSize[0] - xOffset, self._imageSize[1])
        destinationTopLeft = (xOffset, 0)
        destinationTopRight = (self._imageSize[0] - xOffset, 0)
        return np.float32([destinationBottomLeft, destinationTopLeft, destinationTopRight, destinationBottomRight])

    def getSourcePoints(self):
        """Getter for source points

        Results source points representing a trapezoid
        """
        return self._sourcePoints

    def getDestinationPoints(self):
        """Getter for destination points

        Results destination points representing a rectangle
        """
        return self._destinationPoints

    def warp(self, image):
        """Warps an image

        Warps an image using perspective transform
        """
        return cv2.warpPerspective(image, self._transformationMatrix, self._imageSize)

    def unWarp(self, image):
        """Unwarps an image

        Unwarps an image using inverse perspective transform
        """
        return cv2.warpPerspective(image, self._inverseTransformationMatrix, self._imageSize)
