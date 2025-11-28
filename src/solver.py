"""
Wrapper for the Kociemba cube solver.
"""

import sys
from pathlib import Path
from typing import List


def solve_cube(state_str: str) -> List[str]:
    """
    Solve a Rubik's cube using the Kociemba algorithm.
    
    Args:
        state_str: 54-character string representing the cube state in Kociemba format
        
    Returns:
        List of moves (e.g., ["R", "U", "R'", "F2", ...])
        
    Raises:
        ValueError: If state string is invalid
    """
    try:
        import kociemba
    except ImportError:
        raise ImportError("kociemba library not installed. Run: pip install kociemba")
    
    # Validate state string
    if len(state_str) != 54:
        raise ValueError(f"State string must be exactly 54 characters, got {len(state_str)}")
    
    # Validate characters are valid cube colors
    valid_colors = {'U', 'R', 'F', 'D', 'L', 'B'}
    for i, char in enumerate(state_str):
        if char not in valid_colors:
            raise ValueError(f"Invalid character '{char}' at position {i}. Must be one of {valid_colors}")
    
    try:
        # Call Kociemba solver
        solution_str = kociemba.solve(state_str)
        
        # Parse solution string into list of moves
        # Kociemba returns moves separated by spaces, e.g., "R U R' F2 D' L"
        moves = solution_str.strip().split()
        
        return moves
        
    except Exception as e:
        raise ValueError(f"Kociemba solver error: {e}")


def main():
    """
    CLI entry point for the solver.
    """
    # Get state string from command line argument or file
    if len(sys.argv) > 1:
        state_str = sys.argv[1].strip()
        if len(state_str) != 54:
            print(f"Error: State string must be exactly 54 characters, got {len(state_str)}")
            sys.exit(1)
    else:
        # Read from default file
        data_dir = Path(__file__).parent.parent / "data"
        state_file = data_dir / "cube_state.txt"
        
        if not state_file.exists():
            print(f"Error: State file not found: {state_file}")
            print("Please run 'python src/state_builder.py' first, or provide state string as argument.")
            sys.exit(1)
        
        with open(state_file, 'r') as f:
            state_str = f.read().strip()
    
    print("=" * 50)
    print("Cube Solver")
    print("=" * 50)
    print(f"\nState string: {state_str}")
    print("\nSolving...")
    
    try:
        moves = solve_cube(state_str)
        
        print(f"\nSolution found! ({len(moves)} moves)")
        print("\nMoves:")
        for i, move in enumerate(moves, 1):
            print(f"  {i:2d}. {move}")
        
        print(f"\nSolution string: {' '.join(moves)}")
        print("=" * 50)
        
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

