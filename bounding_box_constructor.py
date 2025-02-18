import numpy as np
import cv2

class BoundingBoxConstructor:
    def __init__(self, vanishing_points, camera_matrix):
        self.vanishing_points = vanishing_points
        self.camera_matrix = camera_matrix

    def construct_3d_box(self, bbox_2d, depth, aspect_ratio=None):
        try:
            x1, y1, x2, y2 = bbox_2d
            if x1 >= x2 or y1 >= y2 or depth <= 0 or depth > 1:
                raise ValueError("Invalid bounding box or depth")

            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            width = x2 - x1
            height = y2 - y1

            # Use a default depth if the estimated depth is unreliable
            if depth < 0.1:
                depth = 0.5  # Set a default mid-range depth

            # Estimate 3D dimensions
            width_3d = width * depth * 10  # Scale factor added
            height_3d = height * depth * 10  # Scale factor added

            if aspect_ratio is None:
                length_3d = max(width_3d, height_3d)
            else:
                length_3d = max(width_3d, height_3d) * aspect_ratio

            # Construct 3D bounding box corners
            corners_3d = np.array([
                [-width_3d / 2, -height_3d / 2, length_3d / 2],
                [width_3d / 2, -height_3d / 2, length_3d / 2],
                [width_3d / 2, height_3d / 2, length_3d / 2],
                [-width_3d / 2, height_3d / 2, length_3d / 2],
                [-width_3d / 2, -height_3d / 2, -length_3d / 2],
                [width_3d / 2, -height_3d / 2, -length_3d / 2],
                [width_3d / 2, height_3d / 2, -length_3d / 2],
                [-width_3d / 2, height_3d / 2, -length_3d / 2]
            ])

            # Align with vanishing points
            rotation_matrix = np.column_stack(self.vanishing_points)
            corners_3d = np.dot(corners_3d, rotation_matrix.T)

            # Translate to center position
            corners_3d += np.array([center[0], center[1], depth])

            return corners_3d
        except Exception as e:
            print(f"Error in constructing 3D box: {str(e)}")
            return None

    def project_3d_to_2d(self, corners_3d):
        # Project 3D corners to 2D image plane
        corners_2d, _ = cv2.projectPoints(corners_3d, np.zeros(3), np.zeros(3), self.camera_matrix, None)
        return corners_2d.reshape(-1, 2)