import cv2
import imutils
import numpy as np
import random

class Randomiser:

    def __init__(self, image_path, template=None, tplateXmin=None, tplateYmin=None, tplateXmax=None, tplateYmax=None, threshold = 0.5):
        
        if template is None:
            if(image_path.startswith('http')):
                self.image = imutils.url_to_image(image_path)
            else:
                self.image = cv2.imread(image_path)

            self.template = self.image[tplateYmin:tplateYmax, tplateXmin:tplateXmax]
            self.threshold = threshold
            self.ratio = 1
        else:
            self.image = image
            self.template = template
            self.threshold = threshold
            self.ratio = 1

        self.resized_image = None
        self.resized_template = None
        self.blur_resized_image = None
        self.blur_resized_template = None

        self.resize_width = 300
        (h, w) = self.image.shape[:2]
        if w < self.resize_width:
            self.resize_width = w


    def randomise(self, numberOutputBBoxes = 3):
        self.numberOutputBBoxes = numberOutputBBoxes
        self.preprocessing()
        matches = self.multiTemplateMatching()
        selected = self.randomSelection(matches)
        original = (np.array(selected)*self.ratio).astype(int).tolist()
        return original

    def preprocessing(self):
        #resized
        self.resized_image = imutils.resize(self.image, width = self.resize_width)
        self.ratio = float(self.image.shape[1]) / float(self.resized_image.shape[1])
        (h, w) = self.template.shape[:2]
        self.resized_template = imutils.resize(self.template, int(w/self.ratio))

        # denoising
        # blur_image = cv2.GaussianBlur(image, (3, 3), 0)
        self.blur_resized_image = cv2.medianBlur(self.resized_image, 3)
        self.blur_resized_template = cv2.medianBlur(self.resized_template, 3)
        # self.blur_resized_image = self.grab_cut_segmentation(self.blur_resized_image) 

    @staticmethod
    def compute_iou(a, b, epsilon=1e-5):
        """ Given two boxes `a` and `b` defined as a list of four numbers:
                [x1,y1,x2,y2]
            where:
                x1,y1 represent the upper left corner
                x2,y2 represent the lower right corner
            It returns the Intersect of Union score for these two boxes.

        Args:
            a:          (list of 4 numbers) [x1,y1,x2,y2]
            b:          (list of 4 numbers) [x1,y1,x2,y2]
            epsilon:    (float) Small value to prevent division by zero

        Returns:
            (float) The Intersect of Union score.
        """
        # COORDINATES OF THE INTERSECTION BOX

        x1 = max(a[0], b[0])
        y1 = max(a[1], b[1])
        x2 = min(a[2], b[2])
        y2 = min(a[3], b[3])

        # AREA OF OVERLAP - Area where the boxes intersect
        width = (x2 - x1)
        height = (y2 - y1)
        # handle case where there is NO overlap
        if (width<0) or (height <0):
            return 0.0
        area_overlap = width * height

        # COMBINED AREA
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        area_combined = area_a + area_b - area_overlap

        # RATIO OF AREA OF OVERLAP OVER COMBINED AREA
        iou = area_overlap / (area_combined+epsilon)
        return iou

    @staticmethod
    def non_max_suppression(objects, non_max_suppression_threshold=0.5, score_key=4):
        """
        Filter objects overlapping with IoU over threshold by keeping only the one with maximum score.
        Args:
            objects (List[List]): a list of objects list,
            non_max_suppression_threshold (float): the minimum IoU value used to filter overlapping boxes when
                conducting non max suppression.
            score_key (str): score index in objects list
        Returns:
            List[list]: the filtered list of dictionaries.
        """
        sorted_objects = sorted(objects, key=lambda obj: obj[score_key], reverse=True)
        filtered_objects = []
        for object_ in sorted_objects:
            overlap_found = False
            for filtered_object in filtered_objects:
                iou = Randomiser.compute_iou(object_, filtered_object)
                if iou > non_max_suppression_threshold:
                    overlap_found = True
                    break
            if not overlap_found:
                filtered_objects.append(object_)
        return filtered_objects

    def multiTemplateMatching(self):
        # find all occurrence of template object in the image
        (h, w) = self.blur_resized_template.shape[:2]
        res = cv2.matchTemplate(self.blur_resized_image, self.blur_resized_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.threshold)
        matches = []
        for pt in zip(*loc[::-1]):
            bbox = [pt[0], pt[1], pt[0] + w, pt[1] + h, res[pt[1], pt[0]]]
            matches.append(bbox)

        NMS_THRESHOLD = 0.02
        matches = Randomiser.non_max_suppression(matches, non_max_suppression_threshold=NMS_THRESHOLD, score_key=4)
        return matches

    def randomSelection(self, matches):
        # matchesParts = {}.fromkeys(["{}".format(i) for i in range(self.numberOutputBBoxes)], [])
        matchesParts = [[] for i in range(self.numberOutputBBoxes)]
        (h, w) = self.blur_resized_image.shape[:2]
        factor = int(h / self.numberOutputBBoxes)

        for bbox in matches:
            i = int(bbox[3]/factor)
            if i >= self.numberOutputBBoxes:
                i = self.numberOutputBBoxes - 1
            matchesParts[i].append(bbox)

        selected = []
        for bboxes in matchesParts:
            if len(bboxes) > 0:
                bbox = random.sample(bboxes, 1)
                selected.append(bbox[0])

        return selected
