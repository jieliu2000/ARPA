import easyocr
import cv2
import numpy as np
from difflib import SequenceMatcher

class ImageHandler:
    def __init__(self, debug_mode = False):
        self.debug_mode = debug_mode
        pass
    
    def check_point_inide_rect(self, point, rect):
        '''Check if a point is in a rect. The point's coordinates are (x, y). The rect's coordinates are (x, y, width, height).'''
        if point is None or rect is None:
            return False
        # If the point is inside the rectangle
        return rect[0] <= point[0] <= rect[0] + rect[2] and rect[1] <= point[1] <= rect[1] + rect[3]
    

    def find_text_in_image(self, image, text, rect=None):
        if self.debug_mode:
            cv2.imshow('shapes', np.array(image)) 
            cv2.waitKey(0)
        reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
        arr = reader.readtext(np.array(image))
        (position, target_text, best_ratio) = None, None, 0
        for r in arr:  
            ratio = SequenceMatcher(None, r[1], text).ratio()
            if  text in r[1] and ((rect is not None and self.check_point_inide_rect(r[0][0], rect)) or rect is None):  
                position = r[0]
                target_text = r[1]
                break
            elif ratio > best_ratio and ratio > 0.6 and ((rect is not None and self.check_point_inide_rect(r[0][0], rect)) or rect is None):
                best_ratio = ratio
                target_text = r[1]
                position = r[0]
        #cv2.destroyAllWindows()

        if target_text is None:
            return None, None
        
        return (position[0], position[1])


    def find_window_near_position(self, image, target):
        return self.find_control_near_position(image, target)

    def find_control_near_position(self, image, target):
        img = np.array(image)
        # converting image into grayscale image 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
      
        # setting threshold of gray image 
        edged = cv2.Canny(gray, 50, 200, apertureSize = 5) 

        # using a findContours() function 
        contours, _ = cv2.findContours( 
            edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
        
        if self.debug_mode:
            cv2.drawContours(img, contours, -1, (0, 255, 0), 1) 

        i = 0
        dist = 1000000
        a = 0
        target_information = None
        # list for storing names of shapes 
        for contour in contours: 
            # Approximate contour to a polygon
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)

            # Calculate aspect ratio and bounding box
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)

                if(h<10 and w<10):
                    #ignore too small shapes
                    continue

                dist1 = abs(cv2.pointPolygonTest(contour,(float(target[0]), float(target[1])),True))
            

                if(dist1 < dist):
                    dist = dist1
                    target_information = approx, (x, y, w, h)
        # displaying the image after drawing contours 
        if self.debug_mode:
            cv2.drawContours(img, [target_information[0]], -1, (0, 255, 0), 1)
            cv2.imshow('shapes', img) 
            cv2.waitKey(0)
        if(target_information != None):
            #cv2.destroyAllWindows()
            return target_information[1]
        return None
    