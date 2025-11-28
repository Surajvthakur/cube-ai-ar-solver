"""
Color classifier for mapping HSV values to cube color letters.
"""

import numpy as np
from typing import Dict, List, Tuple
from utils import CUBE_COLORS


class ColorClassifier:
    """
    Classifies HSV color values to cube color letters (R, G, B, O, Y, W).
    Uses the center sticker of each face as a reference color.
    """
    
    def __init__(self):
        """Initialize the classifier with empty reference colors."""
        self.reference_colors: Dict[str, Tuple[float, float, float]] = {}
    
    def fit_from_scan(self, face_hsv_dict: Dict[str, List[List[float]]]) -> None:
        """
        Fit the classifier using scanned face data.
        Uses the center sticker (index 4) of each face as that face's reference HSV.
        
        Args:
            face_hsv_dict: Dictionary mapping face names to lists of 9 HSV triplets
        """
        self.reference_colors = {}
        
        for face_name, hsv_list in face_hsv_dict.items():
            if len(hsv_list) != 9:
                raise ValueError(f"Face {face_name} must have exactly 9 HSV samples")
            
            # Use center sticker (index 4) as reference
            center_hsv = hsv_list[4]
            self.reference_colors[face_name] = tuple(center_hsv)
        
        print(f"Classifier fitted with {len(self.reference_colors)} reference colors")
        for face, hsv in self.reference_colors.items():
            print(f"  {face}: H={hsv[0]:.1f}, S={hsv[1]:.1f}, V={hsv[2]:.1f}")
    
    def _hue_distance(self, h1: float, h2: float) -> float:
        """
        Calculate circular distance between two hue values (0-180 in OpenCV).
        Handles the wraparound at 180/0.
        
        Args:
            h1: First hue value
            h2: Second hue value
            
        Returns:
            Distance between hues (0-90)
        """
        diff = abs(h1 - h2)
        # Handle circular nature of hue
        return min(diff, 180 - diff)
    
    def _hsv_distance(self, hsv1: Tuple[float, float, float], 
                     hsv2: Tuple[float, float, float]) -> float:
        """
        Calculate Euclidean distance in HSV space with proper hue handling.
        
        Args:
            hsv1: First HSV triplet
            hsv2: Second HSV triplet
            
        Returns:
            Distance value (lower = more similar)
        """
        h1, s1, v1 = hsv1
        h2, s2, v2 = hsv2
        
        # Hue distance (circular, normalized to 0-90 range)
        h_dist = self._hue_distance(h1, h2) / 90.0
        
        # Saturation and Value distances (normalized to 0-255 range)
        s_dist = abs(s1 - s2) / 255.0
        v_dist = abs(v1 - v2) / 255.0
        
        # Weighted Euclidean distance
        # Hue is most important, but we weight it less due to circular nature
        distance = np.sqrt((h_dist * 2.0) ** 2 + s_dist ** 2 + v_dist ** 2)
        
        return distance
    
    def classify_hsv(self, hsv: List[float] | Tuple[float, float, float]) -> str:
        """
        Classify a single HSV value to the closest cube color.
        
        Args:
            hsv: HSV triplet (h, s, v)
            
        Returns:
            Color letter: one of ['R', 'G', 'B', 'O', 'Y', 'W']
        """
        if not self.reference_colors:
            raise ValueError("Classifier not fitted. Call fit_from_scan() first.")
        
        hsv_tuple = tuple(hsv)
        min_distance = float('inf')
        closest_face = None
        
        # Find the reference color with minimum distance
        for face_name, ref_hsv in self.reference_colors.items():
            distance = self._hsv_distance(hsv_tuple, ref_hsv)
            if distance < min_distance:
                min_distance = distance
                closest_face = face_name
        
        # Map face name to color letter
        # Standard mapping: U=White, R=Red, F=Green, D=Yellow, L=Orange, B=Blue
        # But we use the actual reference colors, so we need to map faces to standard colors
        # Actually, we should map based on which reference color is closest
        # For now, we'll use a simple approach: map the closest face to its standard color
        
        face_to_color = {
            "U": "W",  # Up = White (typically)
            "R": "R",  # Right = Red
            "F": "G",  # Front = Green
            "D": "Y",  # Down = Yellow
            "L": "O",  # Left = Orange
            "B": "B"   # Back = Blue
        }
        
        return face_to_color.get(closest_face, "W")
    
    def classify_faces(self, face_hsv_dict: Dict[str, List[List[float]]]) -> Dict[str, List[str]]:
        """
        Classify all HSV values for all faces.
        
        Args:
            face_hsv_dict: Dictionary mapping face names to lists of 9 HSV triplets
            
        Returns:
            Dictionary mapping face names to lists of 9 color letters
        """
        classified_faces = {}
        
        for face_name, hsv_list in face_hsv_dict.items():
            color_list = []
            for hsv in hsv_list:
                color = self.classify_hsv(hsv)
                color_list.append(color)
            classified_faces[face_name] = color_list
        
        return classified_faces


def load_and_classify(json_path: str) -> Dict[str, List[str]]:
    """
    Helper function to load scan data, fit classifier, and return classified faces.
    
    Args:
        json_path: Path to cube_scan.json file
        
    Returns:
        Dictionary mapping face names to lists of 9 color letters
    """
    import json
    from pathlib import Path
    
    scan_file = Path(json_path)
    if not scan_file.exists():
        raise FileNotFoundError(f"Scan file not found: {json_path}")
    
    with open(scan_file, 'r') as f:
        face_hsv_dict = json.load(f)
    
    # Fit classifier
    classifier = ColorClassifier()
    classifier.fit_from_scan(face_hsv_dict)
    
    # Classify all faces
    classified_faces = classifier.classify_faces(face_hsv_dict)
    
    return classified_faces


if __name__ == "__main__":
    """
    Test the classifier by loading and classifying a scan.
    """
    import sys
    from pathlib import Path
    
    # Default path
    default_path = Path(__file__).parent.parent / "data" / "cube_scan.json"
    
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = str(default_path)
    
    try:
        classified = load_and_classify(json_path)
        print("\nClassified faces:")
        for face, colors in classified.items():
            print(f"  {face}: {''.join(colors)}")
    except Exception as e:
        print(f"Error: {e}")

