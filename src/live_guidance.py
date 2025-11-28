"""
Main interactive application for real-time cube solving guidance.
"""

import cv2
import sys
from pathlib import Path
from typing import List, Optional
from utils import init_camera, draw_grid, draw_text_with_bg, draw_move_overlay
from solver import solve_cube


def load_cube_state() -> Optional[str]:
    """
    Load cube state from file or prompt user for input.
    
    Returns:
        54-character state string, or None if cancelled
    """
    data_dir = Path(__file__).parent.parent / "data"
    state_file = data_dir / "cube_state.txt"
    
    if state_file.exists():
        with open(state_file, 'r') as f:
            state_str = f.read().strip()
        if len(state_str) == 54:
            print(f"Loaded state from: {state_file}")
            return state_str
    
    # Prompt user for state string
    print("\nCube state file not found or invalid.")
    print("Please provide a 54-character Kociemba state string.")
    print("You can:")
    print("  1. Paste the state string here")
    print("  2. Press Enter to use a solved cube (for testing)")
    print("  3. Type 'q' to quit")
    
    user_input = input("\nState string (or Enter for solved, 'q' to quit): ").strip()
    
    if user_input.lower() == 'q':
        return None
    
    if not user_input:
        # Default to solved cube for testing
        state_str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        print(f"Using solved cube state: {state_str}")
        return state_str
    
    if len(user_input) != 54:
        print(f"Error: State string must be exactly 54 characters, got {len(user_input)}")
        return None
    
    return user_input


def main():
    """
    Main interactive loop for live solving guidance.
    """
    print("=" * 50)
    print("Cube AI Live Solver")
    print("=" * 50)
    
    # Load cube state
    state_str = load_cube_state()
    if state_str is None:
        print("Exiting.")
        return
    
    # Solve the cube
    print("\nSolving cube...")
    try:
        moves = solve_cube(state_str)
        print(f"Solution found! ({len(moves)} moves)")
    except Exception as e:
        print(f"Error solving cube: {e}")
        return
    
    # Initialize camera
    print("\nInitializing camera...")
    camera = init_camera(0)
    if camera is None:
        print("Failed to initialize camera. Exiting.")
        return
    
    print("\n" + "=" * 50)
    print("Live Guidance Started")
    print("=" * 50)
    print("\nControls:")
    print("  SPACE - Confirm you've executed the current move")
    print("  R     - Restart from beginning (when solved)")
    print("  Q     - Quit")
    print("\nStarting in 2 seconds...")
    
    import time
    time.sleep(2)
    
    # State tracking
    current_step = 0
    total_steps = len(moves)
    grid_size = 200
    
    # Main loop
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame from camera")
            break
        
        # Draw grid overlay
        grid_rect = draw_grid(frame, grid_size)
        
        # Check if solved
        if current_step >= total_steps:
            # Show solved message
            draw_text_with_bg(frame, "SOLVED!", (10, 30),
                            font_scale=1.2, color=(0, 255, 0), bg_color=(0, 0, 0))
            draw_text_with_bg(frame, "Press R to restart or Q to quit", (10, 70),
                            font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 0))
        else:
            # Show current move
            current_move = moves[current_step]
            move_text = f"Step {current_step + 1} / {total_steps}: {current_move}"
            draw_text_with_bg(frame, move_text, (10, 30),
                            font_scale=0.8, color=(255, 255, 255), bg_color=(0, 0, 0))
            
            # Draw move overlay (arrow and face highlight)
            draw_move_overlay(frame, current_move, grid_rect)
            
            # Show instructions
            draw_text_with_bg(frame, "Press SPACE to confirm move", (10, 60),
                            font_scale=0.6, color=(200, 200, 200), bg_color=(0, 0, 0))
        
        # Show controls
        draw_text_with_bg(frame, "Q: Quit", (10, frame.shape[0] - 40),
                         font_scale=0.5, color=(150, 150, 150), bg_color=(0, 0, 0))
        
        # Display frame
        cv2.imshow("Cube AI Live Solver", frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            print("\nQuitting...")
            break
        
        elif key == ord(' ') and current_step < total_steps:
            # Confirm move
            current_step += 1
            if current_step < total_steps:
                print(f"Move {current_step}/{total_steps} confirmed: {moves[current_step - 1]}")
            else:
                print("All moves completed! Cube should be solved.")
        
        elif key == ord('r') or key == ord('R'):
            if current_step >= total_steps:
                # Restart
                current_step = 0
                print("\nRestarting from beginning...")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("\n" + "=" * 50)
    print("Session ended")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)

