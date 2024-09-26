import cv2
import numpy as np

class DepthMasker:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.road_mask = None
        self.points = []

    def manual_road_selection(self, frame):
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.points.append((x, y))
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow('Road Selection', frame)

        clone = frame.copy()
        cv2.namedWindow('Road Selection')
        cv2.setMouseCallback('Road Selection', mouse_callback)

        while True:
            cv2.imshow('Road Selection', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                frame = clone.copy()
                self.points = []
            elif key == ord('c'):
                break

        cv2.destroyWindow('Road Selection')

        if len(self.points) > 2:
            mask = np.zeros((self.height, self.width), dtype=np.uint8)
            points = np.array(self.points, dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
            self.road_mask = mask
        else:
            print("Not enough points selected. Using full frame.")
            self.road_mask = np.ones((self.height, self.width), dtype=np.uint8) * 255

    def apply_mask(self, frame):
        if self.road_mask is None:
            raise ValueError("Road mask has not been created. Call manual_road_selection first.")
        return cv2.bitwise_and(frame, frame, mask=self.road_mask)

    def get_mask(self):
        return self.road_mask