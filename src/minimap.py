import cv2
import numpy as np
from src.camera_utils import get_bbox_bottom_center_xy
from src.constants import MINIMAP_TEMPLATE_PNG_PATH


def get_perspective_transform_matrix(court_corners):
    """Computes the perspective transform matrix to map points from the court's perspective to the frame's perspective.
    
    Args:
        court_corners (list or array-like): A list or array of four points (x, y) representing the corners of the court.
        frame_corners (tuple): A tuple (frame_h, frame_w) representing the height and width of the frame.

    Returns:
        numpy.ndarray: The perspective transform matrix (3x3) that maps the court corners to the frame corners.
    """
    frame = cv2.imread(MINIMAP_TEMPLATE_PNG_PATH)
    frame_h, frame_w = frame.shape[:2]

    # Define destination corners (tl, tr, br, bl) as the full size of the input court outline
    src_corners = np.array(court_corners, dtype=np.int32)
    dst_corners = np.array([
        [0, 0],
        [frame_w, 0],
        [frame_w, frame_h],
        [0, frame_h]
    ], dtype=np.int32)

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_corners.astype(np.float32), dst_corners.astype(np.float32))
    return M


def create_minimap(player_bboxes, transform_matrix) -> np.ndarray:
    """Create a minimap showing the bird's eye view of the court and player positions.

    Args:
        frame (np.ndarray): The original video frame.
        court_coords (list): List of court corner coordinates.
        player_bboxes (list): List of player bounding box coordinates.
        minimap_width (float, optional): Width of the minimap as ratio of zoomed frame width

    Returns:
        np.ndarray: The minimap image.
    """
    minimap = cv2.imread('/Users/Henry/Desktop/github/autostream-dupe/data/raw/basketball_court_outline.png')
    minimap = np.array(minimap)

    # Get player locations and convert to NumPy array
    player_locations_xy = np.array([get_bbox_bottom_center_xy(box) for box in player_bboxes], dtype=np.float32).reshape(-1, 1, 2)

    # Apply the perspective transform
    transformed_player_coords = cv2.perspectiveTransform(player_locations_xy, transform_matrix)

    # Draw players on the minimap
    for point in transformed_player_coords:
        x, y = int(point[0][0]), int(point[0][1])
        cv2.circle(minimap, (x, y), radius=5, color=(255, 0, 0), thickness=2)

    return minimap


def add_minimap_to_frame(frame, minimap, minimap_width: float = 0.2) -> np.ndarray:
    """Add a minimap to the frame showing the court and player positions.
    Args:
        frame (np.ndarray): The original video frame.
        minimap (np.ndarray): The minimap image.
    Returns:
        np.ndarray: The frame with the minimap overlay.
    """
    # Scale the minimap to the desired size to be displayed in corner of the frame
    frame_h, frame_w = frame.shape[:2]
    scaled_h = int(minimap_width * frame_h)
    scaled_w = int(minimap_width * frame_w)
    minimap = cv2.resize(minimap, (scaled_w, scaled_h))

    overlay = frame.copy()
    overlay[0:scaled_h, 0:scaled_w] = minimap[..., :3]  # Only take RGB channels
    minimap_alpha = 0.9
    frame = cv2.addWeighted(overlay, minimap_alpha, frame, 1-minimap_alpha, 0)  # Blend the minimap with the frame
    return frame


