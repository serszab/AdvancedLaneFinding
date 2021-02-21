import numpy as np
import cv2

class GradientsAndColor:
    def __init__(self, image):
        self._image = image
        self._hlsImage = cv2.cvtColor(np.copy(image), cv2.COLOR_RGB2HLS)
        self._hsvImage = cv2.cvtColor(np.copy(image), cv2.COLOR_RGB2HSV)

    def colorAndGradientFiltering(self):
        binaryImage = np.zeros_like(self._image[:,:,0])
        binaryImage[self._mask()] = 1
        return np.dstack((binaryImage, binaryImage, binaryImage)) * 255
    
    def _sobelXInLChannel(self, lowThreshold, highThreshold):
        sobelX = cv2.Sobel(self._hlsImage[:,:,1], cv2.CV_64F, 1, 0)
        absSobelX = np.absolute(sobelX)
        scaledSobel = np.uint8(255 * absSobelX / np.max(absSobelX))
        return ((lowThreshold <= scaledSobel) & (scaledSobel <= highThreshold))

    def _sChannel(self, lowThreshold, highThreshold):
        sChannel = self._hlsImage[:,:,2]
        return ((lowThreshold <= sChannel) & (sChannel <= highThreshold))

    def _yellowLanes(self, lowThreshold, highThreshold):
        hChannel = self._hsvImage[:,:,0]
        sChannel = self._hsvImage[:,:,1]
        vChannel = self._hsvImage[:,:,2]
        return ((lowThreshold[0] < hChannel) & (hChannel < highThreshold[0]) & (lowThreshold[1] < sChannel) & (sChannel < highThreshold[1]) & (lowThreshold[2] < vChannel) & (vChannel < highThreshold[2]))

    def _mask(self):
        return self._sobelXInLChannel(20, 100) | self._sChannel(170, 255) | self._yellowLanes([0, 80, 200],[40, 255, 255])