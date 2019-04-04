import cv2 as cv2
import numpy as np
from scipy.spatial import distance as dist
import math
from enum import Enum
# import random 

try:
    from cv2 import cv2
except ImportError:
    pass

class DIRECTION(Enum):
    LEFT = 0
    RIGHT = 1

class VisionTape:
    def __init__(self, image, imageCornerLoc, contour):
        self.image = image
        self.imageCorner = imageCornerLoc
        self.minAreaRect = None
        self.contour = contour
        self.center = None
        self.points = []
        self.corners = []
        self.direction = None

    def get_center(self):
        """
        Get the centroid of the minimum area rectangle
        that surrounds this contour

        Returns:
            The center in the form (x, y)
        """

        if(self.minAreaRect is None):
            self.determine_direction(self.contour)
        
        # print("center pos:")
        # print(self.minAreaRect[0])

        return self.minAreaRect[0]

    def get_area(self):
        contour = self.contour
        return cv2.contourArea(contour)



    def get_x_center_coordinate(self):
        if(self.minAreaRect is None):
            self.determine_direction(self.contour)
        
        return self.get_center()[0]


    def get_angle(self):
        """
        Get the angle of the min area rectangle surrounding this contour

        Returns:
            The angle with zero straight up, positive clockwise
        """
        if self.direction is None:
            self.determine_direction(self.contour)
        
        return self.minAreaRect[2]

    def get_direction(self):
        """
        Get the direction of the min area rectangle surrounding this contour

        Returns:
            The direction, left/right
        """
        if self.direction is None:
            self.determine_direction(self.contour)
        
        return self.direction



    def determine_direction(self, contour):

        minRect = cv2.minAreaRect(contour)

        while(minRect[2] < -45):
            dims = minRect[1]
            dims = [dims[1], dims[0]]
            minRect = (minRect[0], dims, minRect[2] + 90)
        while(minRect[2] > 45):
            dims = minRect[1]
            dims = [dims[1], dims[0]]
            minRect = (minRect[0], dims, minRect[2] - 90)

        self.minAreaRect = minRect

        if(minRect[2] > 0):
            self.direction = DIRECTION.RIGHT
        else:
            self.direction = DIRECTION.LEFT

        self.minAreaRect = minRect
        return minRect

    # @staticmethod
    # def compare(item1, item2):
    #     # this needs to return -1 if it's less than the other, 0 if same, or 1 of greater than other
    #     if item1.get_center()[1] < item2.get_center()[1]:
    #         return -1
    #     elif item1.get_center()[1] > item2.get_center()[1]:
    #         return 1
    #     else:
    #         return 0



    def order_points(self, pts):

        # TODO Change sort to Y axis then x axis

        ySorted= pts[np.argsort(pts[:, 1]), :]
        print("sorted by y axis: %s" % ySorted)

        # # sort the points based on their x-coordinates
        # xSorted = pts[np.argsort(pts[:, 0]), :]

        # # grab the left-most and right-most points from the sorted
        # # x-roodinate points
        # leftMost = xSorted[:2, :]
        # rightMost = xSorted[2:, :]

        # # now, sort the left-most coordinates according to their
        # # y-coordinates so we can grab the top-left and bottom-left
        # # points, respectively
        # leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        # (tl, bl) = leftMost

        # # now that we have the top-left coordinate, use it as an
        # # anchor to calculate the Euclidean distance between the
        # # top-left and right-most points; by the Pythagorean
        # # theorem, the point with the largest distance will be
        # # our bottom-right point
        # D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        # (br, tr) = rightMost[np.argsort(D)[::-1], :]

        # # return the coordinates in top-left, top-right,
        # # bottom-right, and bottom-left order

        # self.orderedPoints = np.array([tl, tr, br, bl], dtype="float32")

        # img = cv2.pyrDown(cv2.imread("/Users/matt/Documents/GitHub/pantry-vision/images/2019/CargoStraightDark72in.jpg",
        #                              cv2.IMREAD_UNCHANGED))
        # cv2.circle(img, (tl), 4, (255, 0, 0), -1)

        # cv2.imshow(img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # return self.orderedPoints

class VisionTarget:
    def __init__(self, individualTapes):
        """
        A vision target, consisting of two indivitual VisionTape objects
        
        Args:
            individualTapes in the form left, right
        
        """
        self.individualTapes = individualTapes
        self.hull = None

    def get_area(self):
        return sum(f.get_area() for f in self.individualTapes)

    # @staticmethod
    def get_center(self):
        centerX = (self.individualTapes[0].get_center()[0] + self.individualTapes[1].get_center()[0])/2
        centerY = (self.individualTapes[0].get_center()[1] + self.individualTapes[1].get_center()[1])/2

        return [centerX, centerY]

    def get_center_offset(self, res):
        xCoord = self.get_center()[0]
        return xCoord - (res/2.0)

        # i guess just the average of the two centers

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """

    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__hsv_threshold_hue = [15.9558030341169, 137.8198178573477]
        self.__hsv_threshold_saturation = [65.519019296701, 255.0]
        self.__hsv_threshold_value = [69.45015658363164, 255.0]

        self.hsv_threshold_output = None

        self.__find_contours_input = self.hsv_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 10.0
        self.__filter_contours_min_perimeter = 0.0
        self.__filter_contours_min_width = 0.0
        self.__filter_contours_max_width = 1000.0
        self.__filter_contours_min_height = 0.0
        self.__filter_contours_max_height = 1000.0
        self.__filter_contours_solidity = [0.0, 100]
        self.__filter_contours_max_vertices = 1000000.0
        self.__filter_contours_min_vertices = 0.0
        self.__filter_contours_min_ratio = 0.0
        self.__filter_contours_max_ratio = 20.0

        self.filter_contours_output = None
        self.__hsv_threshold_input = None

        self.boundingRects = None
        self.visionTapes = []
        self.visionPair = None

    def process(self, source0, horizontalRes = 320):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSV_Threshold0:
        self.__hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue,
                                                           self.__hsv_threshold_saturation, self.__hsv_threshold_value)

        # Step Find_Contours0:
        self.__find_contours_input = self.hsv_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input,
                                                           self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours,
                                                               self.__filter_contours_min_area,
                                                               self.__filter_contours_min_perimeter,
                                                               self.__filter_contours_min_width,
                                                               self.__filter_contours_max_width,
                                                               self.__filter_contours_min_height,
                                                               self.__filter_contours_max_height,
                                                               self.__filter_contours_solidity,
                                                               self.__filter_contours_max_vertices,
                                                               self.__filter_contours_min_vertices,
                                                               self.__filter_contours_min_ratio,
                                                               self.__filter_contours_max_ratio)

        self.boundingRects = self.getRect(self.filter_contours_output)

        for i, rect in enumerate(self.boundingRects):
            self.visionTapes.append(
                VisionTape(
                    self.crop(source0.copy(), rect), [rect[0], rect[1]], self.filter_contours_output[i]
                )
            )
        
        self.visionTapes = self.sortVisionTargets(self.visionTapes)

        # pair targets up
        self.visionPairs = self.decideVisionPairs(self.visionTapes, horizontalRes)

        # for debugging, annotate the image
        temp = source0.copy()
        # for f in self.visionPairs:
        loc = self.visionPairs.get_center()
        loc = np.int0(loc)
        loc = (loc[0], loc[1])
        cv2.circle(temp, tuple(loc), 3, (0,0,255))
        cv2.line(temp, tuple(np.int0(self.visionPairs.individualTapes[0].get_center())), tuple(np.int0(self.visionPairs.individualTapes[1].get_center())), (255, 255, 0))

        self.printVisionTapes(self.visionTapes)

  
        for e in self.visionTapes:
            loc = e.get_center()
            loc = np.int0(loc)
            loc = (loc[0], loc[1])
            cv2.circle(temp, tuple(loc), 3, (255,0,0))
            

        cv2.namedWindow('temp',cv2.WINDOW_GUI_EXPANDED)
        cv2.imshow('temp', temp)
        cv2.resizeWindow('temp', 800,600)


    @staticmethod
    def printVisionTapes(sortedList):
        for i, item in enumerate(sortedList):
            print(item.get_x_center_coordinate())

    @staticmethod
    def decideVisionPairs(sortedList, horizontalRes):
        # first, eliminate one off targets hanging out on the edges

        # print(sortedList[0].get_direction())

        if sortedList[0].get_x_center_coordinate() < horizontalRes/2.0 and sortedList[0].get_direction() is DIRECTION.LEFT:
                del(sortedList[0])


        if sortedList[len(sortedList) - 1].get_x_center_coordinate() > horizontalRes/2.0 and sortedList[len(sortedList) - 1].get_direction() is DIRECTION.RIGHT:
            del(sortedList[len(sortedList) - 1])

        assert(len(sortedList) % 2 == 0)

        # from here, just kinda loop gang
        pairs = []

        for i in range(0,len(sortedList) - 1,2):
            # print("HULLO")
            # print(i)
            target = VisionTarget([sortedList[i], sortedList[i+1]])
            target.get_center()
            pairs.append(target)

        # pairs = sorted(pairs, key = VisionTape.get_area)

        # uncomment me to sort by area!
        return max(pairs, key = VisionTarget.get_area)
        # sort by offset from center
        # return min(pairs, key = lambda target : abs(target.get_center_offset(horizontalRes)))

        # return pairs

    @staticmethod
    def sortVisionTargets(listOfTargets):
        sortedList = sorted(listOfTargets, key = VisionTape.get_x_center_coordinate)
        # for i, item in enumerate(sortedList):
        #     print(item.get_x_center_coordinate())
        return sortedList

    # get a bounding rectangle
    @staticmethod
    def getRect(contours_):
        """
        Get the bouding rectangles (parallel to X and Y axis) of a list
        of countours
        
        Args:
            contours_: a list of contours

        Returns:
            a list of rectangles in the form [x, y, x_2, y_2], where x_2 and y_2 are the bottom-right corner
        """
        toReturn = []

        for c in contours_:
            # get the bounding rect
            x, y, w, h = cv2.boundingRect(c)

            buffer = 7
            # x,y is top left of the box boi
            x -= int(buffer/2)
            y -= int(buffer/2)
            w += buffer
            h += buffer

            # draw a green rectangle to visualize the bounding rect
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)

            toReturn.append([x, y, x+w, y+h])
        
        return toReturn

    @staticmethod
    def crop(img_, range_):
        """
        """
        img_ = img_[range_[1]:range_[3], range_[0]:range_[2]]

        # print(img_)

        return img_

    @staticmethod
    def __hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.

        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.

        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]), (hue[1], sat[1], val[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if (external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours, hierarchy = cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                          min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                          min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

    # Now we get to do the fun stuff of splitting the detected contours
    # up into their individual parts
    @staticmethod
    def __split_image(image, contours):
        """Splits the image up into individual regions and saves it to a VisionTape object
        Args:
            image: the image we took
            contours: the contours we filtered
        Returns:
            The vision tapes as a list of VisionTapes
        """







pipe = GripPipeline()

loadedImage = cv2.pyrDown(cv2.imread("/Users/matt/Documents/GitHub/pantry-vision/images/2019/CargoStraightDark72in.jpg",
                             cv2.IMREAD_UNCHANGED))

pipe.process(loadedImage, horizontalRes = 320)

# cropped = loadedImage.copy()

# toAnnotate = pipe.hsv_threshold_output

cv2.imshow('before', pipe.hsv_threshold_output)

# contours = pipe.filter_contours_output

# contours = np.asarray(contours)

# # get a bounding rectangle
# def getRect(contours_):

#     toReturn = []

#     for c in contours_:
#         # get the bounding rect
#         x, y, w, h = cv2.boundingRect(c)

#         buffer = 7
#         # x,y is top left of the box boi
#         x -= int(buffer/2)
#         y -= int(buffer/2)
#         w += buffer
#         h += buffer

#         # draw a green rectangle to visualize the bounding rect
#         # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)

#         toReturn.append([x, y, x+w, y+h])
    
#     return toReturn

# def crop(img_, range_):
#     img_ = img_[range_[1]:range_[3], range_[0]:range_[2]]

#     # print(img_)

#     return img_

# a list of rectangles
# rectangles = getRect(contours)

# # a list of cropped images
# visionTape = []

# for rect in rectangles:
#     newimg = crop(cropped, rect)
#     visionTape.append(newimg)

# visionTapeConers = []

# # find the harris corners and subpixel corners
# for iteration, tape in enumerate(visionTape):
#     # find Harris corners
#     gray = cv2.cvtColor(tape, cv2.COLOR_BGR2GRAY)
#     gray = np.float32(gray)
#     dst = cv2.cornerHarris(gray, 2, 3, 0.04)
#     # dst = cv2.goodFeaturesToTrack(gray, 4, 0.05, 2.0, useHarrisDetector=True)
#     dst = cv2.dilate(dst,None)
#     ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
#     dst = np.uint8(dst)

#     # find centroids
#     ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

#     # define the criteria to stop and refine the corners
#     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
#     corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)


#     corners = np.delete(corners, (0), axis=0)

#     visionTapeConers.append(corners)

#     aTape = VisionTape(None, [0,0], contours[iteration]);
#     aTape.determine_direction(aTape.contour)

#     # print(corners.shape)
#     # print("centroids")
#     # print(centroids)

#     # Now draw them
#     # res = np.hstack((corners))
#     corners = np.int0(corners)
#     # print(corners)
#     tape[corners[:,1],corners[:,0]]=[0, 0, 255]
#     tape[corners[:,1],corners[:,0]] = [0, 255, 0]

# annotatedImage = loadedImage.copy()

# # shift the corners over so that their coordinates are back in the global scope
# for i, corner in enumerate(visionTapeConers):
    
#     rect = rectangles[i]
#     x = rect[0]
#     y = rect[1]

#     # cycle through all the corners and offset them
#     for c in corner:
#         c[0] += x
#         c[1] += y

    
#     # print("CORNER: ")
#     # print(corner)

#     for point in corner:
#         # print(point)
#         annotatedImage[int(point[1]), int(point[0])] = [0, 0, 255]

    


# # to display all the images
# for i, tape in enumerate(visionTape):
#     cv2.namedWindow("tape %s" % i,cv2.WINDOW_GUI_EXPANDED)
#     cv2.resizeWindow("tape %s" % i, 400,600)

#     cv2.imshow("tape %s" % i, tape)








# print(boxes)



cv2.waitKey(0)

cv2.destroyAllWindows()


