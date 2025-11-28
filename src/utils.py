"""
Utility functions for cube scanning and visualization.
"""

import cv2
import numpy as np
from typing import Tuple, Optional

# Constants
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
CUBE_COLORS = ["R", "G", "B", "O", "Y", "W"]  # Red, Green, Blue, Orange, Yellow, White

# Color mappings for visualization (BGR format for OpenCV)
COLOR_BGR = {
    "R": (0, 0, 255),      # Red
    "G": (0, 255, 0),      # Green
    "B": (255, 0, 0),      # Blue
    "O": (0, 165, 255),    # Orange
    "Y": (0, 255, 255),    # Yellow
    "W": (255, 255, 255),  # White
}

# Arrow colors for move visualization
ARROW_COLOR_CW = (0, 255, 0)    # Green for clockwise
ARROW_COLOR_CCW = (0, 0, 255)   # Red for counter-clockwise
ARROW_COLOR_DOUBLE = (0, 255, 255)  # Yellow for double turn

# Default grid size
DEFAULT_GRID_SIZE = 200


def init_camera(index: int = 0) -> Optional[cv2.VideoCapture]:
    """
    Safely initialize and return a camera capture object.
    
    Args:
        index: Camera index (default 0 for default webcam)
        
    Returns:
        VideoCapture object if successful, None otherwise
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Error: Could not open camera {index}")
        return None
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    return cap


def draw_grid(frame: np.ndarray, grid_size: int = DEFAULT_GRID_SIZE) -> Tuple[int, int, int, int]:
    """
    Draw a centered 3×3 grid on the frame.
    
    Args:
        frame: Input frame to draw on
        grid_size: Size of the grid in pixels (width and height)
        
    Returns:
        Tuple (x, y, w, h) representing the grid rectangle coordinates
    """
    h, w = frame.shape[:2]
    
    # Calculate center position
    x = (w - grid_size) // 2
    y = (h - grid_size) // 2
    
    # Draw outer rectangle
    cv2.rectangle(frame, (x, y), (x + grid_size, y + grid_size), (255, 255, 255), 2)
    
    # Draw grid lines (3×3 = 2 vertical + 2 horizontal lines)
    cell_size = grid_size // 3
    
    # Vertical lines
    for i in range(1, 3):
        x_line = x + i * cell_size
        cv2.line(frame, (x_line, y), (x_line, y + grid_size), (255, 255, 255), 1)
    
    # Horizontal lines
    for i in range(1, 3):
        y_line = y + i * cell_size
        cv2.line(frame, (x, y_line), (x + grid_size, y_line), (255, 255, 255), 1)
    
    return (x, y, grid_size, grid_size)


def draw_text_with_bg(frame: np.ndarray, text: str, position: Tuple[int, int],
                      font_scale: float = 0.7, color: Tuple[int, int, int] = (255, 255, 255),
                      bg_color: Tuple[int, int, int] = (0, 0, 0), thickness: int = 2) -> None:
    """
    Draw text with a background rectangle for better readability.
    
    Args:
        frame: Frame to draw on
        text: Text string to display
        position: (x, y) position of text
        font_scale: Font scale factor
        color: Text color (BGR)
        bg_color: Background rectangle color (BGR)
        thickness: Text thickness
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    x, y = position
    
    # Draw background rectangle
    cv2.rectangle(frame, 
                  (x - 5, y - text_height - 5),
                  (x + text_width + 5, y + baseline + 5),
                  bg_color, -1)
    
    # Draw text
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)


def draw_move_overlay(frame: np.ndarray, move: str, grid_rect: Tuple[int, int, int, int]) -> None:
    """
    Draw a visual overlay indicating which face to turn and the direction.
    
    Args:
        frame: Frame to draw on
        move: Move string (e.g., "R", "U'", "F2")
        grid_rect: (x, y, w, h) of the grid rectangle
    """
    x, y, w, h = grid_rect
    cell_size = w // 3
    center_x = x + w // 2
    center_y = y + h // 2
    
    # Parse move
    face = move[0]  # U, R, F, D, L, B
    is_double = "2" in move
    is_ccw = "'" in move or "2" in move  # For visualization, we'll handle 2 separately
    
    # Determine arrow color
    if is_double:
        arrow_color = ARROW_COLOR_DOUBLE
    elif is_ccw:
        arrow_color = ARROW_COLOR_CCW
    else:
        arrow_color = ARROW_COLOR_CW
    
    # Map face to grid region and arrow direction
    arrow_length = cell_size // 2
    arrow_thickness = 3
    
    if face == "U":  # Top face - draw arrow at top edge
        start_x = center_x
        start_y = y + cell_size // 2
        if is_double:
            # Draw double arrow (two arrows)
            end_x1 = start_x - arrow_length // 2
            end_y1 = start_y - arrow_length // 2
            end_x2 = start_x + arrow_length // 2
            end_y2 = start_y - arrow_length // 2
            cv2.arrowedLine(frame, (start_x, start_y), (end_x1, end_y1), arrow_color, arrow_thickness, tipLength=0.3)
            cv2.arrowedLine(frame, (start_x, start_y), (end_x2, end_y2), arrow_color, arrow_thickness, tipLength=0.3)
        elif is_ccw:
            end_x = start_x - arrow_length
            end_y = start_y - arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        else:
            end_x = start_x + arrow_length
            end_y = start_y - arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        # Highlight top row
        cv2.rectangle(frame, (x, y), (x + w, y + cell_size), (255, 255, 0), 2)
            
    elif face == "D":  # Bottom face - draw arrow at bottom edge
        start_x = center_x
        start_y = y + h - cell_size // 2
        if is_double:
            end_x1 = start_x - arrow_length // 2
            end_y1 = start_y + arrow_length // 2
            end_x2 = start_x + arrow_length // 2
            end_y2 = start_y + arrow_length // 2
            cv2.arrowedLine(frame, (start_x, start_y), (end_x1, end_y1), arrow_color, arrow_thickness, tipLength=0.3)
            cv2.arrowedLine(frame, (start_x, start_y), (end_x2, end_y2), arrow_color, arrow_thickness, tipLength=0.3)
        elif is_ccw:
            end_x = start_x + arrow_length
            end_y = start_y + arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        else:
            end_x = start_x - arrow_length
            end_y = start_y + arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        # Highlight bottom row
        cv2.rectangle(frame, (x, y + h - cell_size), (x + w, y + h), (255, 255, 0), 2)
            
    elif face == "L":  # Left face - draw arrow at left edge
        start_x = x + cell_size // 2
        start_y = center_y
        if is_double:
            end_x1 = start_x - arrow_length // 2
            end_y1 = start_y - arrow_length // 2
            end_x2 = start_x - arrow_length // 2
            end_y2 = start_y + arrow_length // 2
            cv2.arrowedLine(frame, (start_x, start_y), (end_x1, end_y1), arrow_color, arrow_thickness, tipLength=0.3)
            cv2.arrowedLine(frame, (start_x, start_y), (end_x2, end_y2), arrow_color, arrow_thickness, tipLength=0.3)
        elif is_ccw:
            end_x = start_x - arrow_length
            end_y = start_y + arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        else:
            end_x = start_x - arrow_length
            end_y = start_y - arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        # Highlight left column
        cv2.rectangle(frame, (x, y), (x + cell_size, y + h), (255, 255, 0), 2)
            
    elif face == "R":  # Right face - draw arrow at right edge
        start_x = x + w - cell_size // 2
        start_y = center_y
        if is_double:
            end_x1 = start_x + arrow_length // 2
            end_y1 = start_y - arrow_length // 2
            end_x2 = start_x + arrow_length // 2
            end_y2 = start_y + arrow_length // 2
            cv2.arrowedLine(frame, (start_x, start_y), (end_x1, end_y1), arrow_color, arrow_thickness, tipLength=0.3)
            cv2.arrowedLine(frame, (start_x, start_y), (end_x2, end_y2), arrow_color, arrow_thickness, tipLength=0.3)
        elif is_ccw:
            end_x = start_x + arrow_length
            end_y = start_y - arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        else:
            end_x = start_x + arrow_length
            end_y = start_y + arrow_length
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        # Highlight right column
        cv2.rectangle(frame, (x + w - cell_size, y), (x + w, y + h), (255, 255, 0), 2)
            
    elif face == "F":  # Front face - draw arrow in center
        start_x = center_x
        start_y = center_y
        if is_double:
            # Draw circular double arrow
            radius = arrow_length
            cv2.circle(frame, (start_x, start_y), radius, arrow_color, arrow_thickness)
            cv2.putText(frame, "x2", (start_x - 15, start_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, arrow_color, 2)
        elif is_ccw:
            end_x = start_x - arrow_length
            end_y = start_y
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        else:
            end_x = start_x + arrow_length
            end_y = start_y
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)
        # Highlight center (front face)
        cv2.rectangle(frame, (x + cell_size, y + cell_size), 
                     (x + 2 * cell_size, y + 2 * cell_size), (255, 255, 0), 2)
            
    elif face == "B":  # Back face - draw outline around entire grid
        cv2.rectangle(frame, (x - 5, y - 5), (x + w + 5, y + h + 5), (255, 255, 0), 3)
        # Draw arrow indicator
        start_x = x + w + 20
        start_y = center_y
        if is_double:
            cv2.putText(frame, "B2", (start_x, start_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, arrow_color, 2)
        else:
            end_x = start_x + arrow_length
            end_y = start_y
            cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), arrow_color, arrow_thickness, tipLength=0.3)

