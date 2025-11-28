"""
Build a 54-character Kociemba state string from classified cube faces.
"""

from typing import Dict, List
from pathlib import Path
from color_classifier import load_and_classify
from utils import FACE_ORDER, CUBE_COLORS


def build_kociemba_string(faces: Dict[str, List[str]]) -> str:
    """
    Convert faces dict into a 54-char string in Kociemba facelet order.
    
    Kociemba facelet order:
    - U face: positions 0-8   (top face, row by row: 0,1,2,3,4,5,6,7,8)
    - R face: positions 9-17  (right face)
    - F face: positions 18-26  (front face)
    - D face: positions 27-35  (down face)
    - L face: positions 36-44  (left face)
    - B face: positions 45-53  (back face)
    
    Each face is stored as a 3×3 grid in row-major order:
    [0, 1, 2,
     3, 4, 5,
     6, 7, 8]
    
    Args:
        faces: Dictionary mapping face names to lists of 9 color letters
               Keys: 'U', 'R', 'F', 'D', 'L', 'B'
               Values: Lists of 9 color letters (R, G, B, O, Y, W)
    
    Returns:
        54-character string representing the cube state
    
    Raises:
        ValueError: If input is invalid (wrong number of faces, wrong length, wrong color counts)
    """
    # Validate input
    if len(faces) != 6:
        raise ValueError(f"Expected exactly 6 faces, got {len(faces)}")
    
    # Check that all required faces are present
    for face in FACE_ORDER:
        if face not in faces:
            raise ValueError(f"Missing face: {face}")
    
    # Validate each face has 9 entries
    for face_name, color_list in faces.items():
        if len(color_list) != 9:
            raise ValueError(f"Face {face_name} must have exactly 9 colors, got {len(color_list)}")
        
        # Validate all colors are valid
        for color in color_list:
            if color not in CUBE_COLORS:
                raise ValueError(f"Invalid color '{color}' in face {face_name}. Must be one of {CUBE_COLORS}")
    
    # Count total occurrences of each color
    color_counts = {}
    for face_colors in faces.values():
        for color in face_colors:
            color_counts[color] = color_counts.get(color, 0) + 1
    
    # Validate exactly 9 of each color
    for color in CUBE_COLORS:
        count = color_counts.get(color, 0)
        if count != 9:
            raise ValueError(f"Expected exactly 9 '{color}' stickers, got {count}")
    
    # Build the 54-character string in Kociemba order
    state_string = ""
    
    for face_name in FACE_ORDER:
        face_colors = faces[face_name]
        # Append all 9 colors for this face
        state_string += "".join(face_colors)
    
    # Final validation
    if len(state_string) != 54:
        raise ValueError(f"State string must be exactly 54 characters, got {len(state_string)}")
    
    return state_string


def main():
    """
    Main function: load scan data, classify colors, build state string.
    """
    import sys
    
    # Default paths
    data_dir = Path(__file__).parent.parent / "data"
    scan_file = data_dir / "cube_scan.json"
    output_file = data_dir / "cube_state.txt"
    
    # Check if scan file exists
    if not scan_file.exists():
        print(f"Error: Scan file not found: {scan_file}")
        print("Please run 'python src/scanner.py' first to scan the cube.")
        sys.exit(1)
    
    print("=" * 50)
    print("Building Cube State")
    print("=" * 50)
    
    try:
        # Load and classify faces
        print(f"\nLoading scan data from: {scan_file}")
        classified_faces = load_and_classify(str(scan_file))
        
        print("\nClassified faces:")
        for face_name in FACE_ORDER:
            colors = classified_faces[face_name]
            # Display as 3×3 grid
            print(f"  {face_name}: {colors[0]}{colors[1]}{colors[2]}")
            print(f"      {colors[3]}{colors[4]}{colors[5]}")
            print(f"      {colors[6]}{colors[7]}{colors[8]}")
        
        # Build Kociemba string
        print("\nBuilding Kociemba state string...")
        state_string = build_kociemba_string(classified_faces)
        
        print(f"\nState string (54 characters):")
        print(state_string)
        
        # Save to file
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(state_string)
        
        print(f"\nState saved to: {output_file}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

