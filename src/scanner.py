"""
Interactive scanner for capturing all 6 faces of a Rubik's Cube.
"""

import cv2
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple
from utils import init_camera, draw_grid, draw_text_with_bg, FACE_ORDER


def sample_cell_hsv(frame: np.ndarray, cell_x: int, cell_y: int, cell_size: int) -> Tuple[float, float, float]:
    """
    Sample the average HSV value from a grid cell.
    
    Args:
        frame: Input frame (BGR format)
        cell_x: X coordinate of cell top-left corner
        cell_y: Y coordinate of cell top-left corner
        cell_size: Size of the cell in pixels
        
    Returns:
        Tuple (h, s, v) representing average HSV values
    """
    # Extract cell region (leave small margin to avoid edges)
    margin = cell_size // 10
    roi = frame[cell_y + margin:cell_y + cell_size - margin,
                cell_x + margin:cell_x + cell_size - margin]
    
    # Convert to HSV
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Calculate mean HSV values
    h_mean = np.mean(hsv_roi[:, :, 0])
    s_mean = np.mean(hsv_roi[:, :, 1])
    v_mean = np.mean(hsv_roi[:, :, 2])
    
    return (float(h_mean), float(s_mean), float(v_mean))


def capture_face(face_name: str, camera: cv2.VideoCapture) -> List[List[float]]:
    """
    Interactive capture for one cube face.
    
    Args:
        face_name: Name of the face being captured (U, R, F, D, L, B)
        camera: VideoCapture object
        
    Returns:
        List of 9 HSV triplets, one for each cell in the 3×3 grid
    """
    print(f"\nCapturing face {face_name}...")
    print("Align the cube face inside the grid and press SPACE to capture.")
    print("Press Q to quit.")
    
    grid_size = 200
    hsv_samples = []
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame from camera")
            break
        
        # Draw grid overlay
        grid_rect = draw_grid(frame, grid_size)
        x, y, w, h = grid_rect
        cell_size = w // 3
        
        # Draw instructions
        instruction = f"Align face {face_name} inside the grid"
        draw_text_with_bg(frame, instruction, (10, 30), 
                         font_scale=0.8, color=(255, 255, 255), bg_color=(0, 0, 0))
        draw_text_with_bg(frame, "Press SPACE to capture, Q to quit", (10, 60),
                         font_scale=0.6, color=(200, 200, 200), bg_color=(0, 0, 0))
        
        # Display frame
        cv2.imshow("Cube Scanner", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # SPACE pressed
            # Sample HSV from each of the 9 cells
            hsv_samples = []
            for row in range(3):
                for col in range(3):
                    cell_x = x + col * cell_size
                    cell_y = y + row * cell_size
                    hsv = sample_cell_hsv(frame, cell_x, cell_y, cell_size)
                    hsv_samples.append(list(hsv))
            
            print(f"Face {face_name} captured! HSV samples:")
            for i, hsv in enumerate(hsv_samples):
                print(f"  Cell {i}: H={hsv[0]:.1f}, S={hsv[1]:.1f}, V={hsv[2]:.1f}")
            
            # Show confirmation
            frame_copy = frame.copy()
            draw_text_with_bg(frame_copy, f"Face {face_name} captured!", (10, 30),
                            font_scale=0.8, color=(0, 255, 0), bg_color=(0, 0, 0))
            cv2.imshow("Cube Scanner", frame_copy)
            cv2.waitKey(1000)  # Show confirmation for 1 second
            
            break
            
        elif key == ord('q') or key == ord('Q'):
            print("Scanning cancelled by user")
            return None
    
    return hsv_samples


def main():
    """
    Main function to capture all 6 faces of the cube.
    """
    print("=" * 50)
    print("Cube Face Scanner")
    print("=" * 50)
    print("\nYou will be guided through capturing all 6 faces.")
    print("Face order: U (Up), R (Right), F (Front), D (Down), L (Left), B (Back)")
    print("\nFor each face:")
    print("  1. Hold the cube so the face is visible")
    print("  2. Align it inside the white grid on screen")
    print("  3. Press SPACE to capture")
    print("  4. Press Q at any time to quit")
    print("\nStarting in 3 seconds...")
    
    import time
    time.sleep(3)
    
    # Initialize camera
    camera = init_camera(0)
    if camera is None:
        print("Failed to initialize camera. Exiting.")
        return
    
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Capture all faces
    face_data = {}
    all_captured = True
    
    for face_name in FACE_ORDER:
        hsv_samples = capture_face(face_name, camera)
        
        if hsv_samples is None:
            print(f"\nScanning cancelled. Partial data will not be saved.")
            all_captured = False
            break
        
        face_data[face_name] = hsv_samples
    
    # Release camera
    camera.release()
    cv2.destroyAllWindows()
    
    # Save data if all faces were captured
    if all_captured:
        output_file = data_dir / "cube_scan.json"
        with open(output_file, 'w') as f:
            json.dump(face_data, f, indent=2)
        
        print("\n" + "=" * 50)
        print("Scan complete!")
        print(f"Data saved to: {output_file}")
        print("=" * 50)
    else:
        print("\nScanning incomplete. No data saved.")


if __name__ == "__main__":
    main()

