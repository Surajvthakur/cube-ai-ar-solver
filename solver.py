# solver.py
import kociemba

# ---- Validate 54-character cube state ----
def validate_state(state):
    if len(state) != 54:
        return False, "State must be 54 characters long."

    # Each color must appear exactly 9 times
    for color in "URFDLB":
        if state.count(color) != 9:
            return False, f"Color {color} count invalid (must be 9)."

    return True, None


# ---- Core function ----
def solve_cube(state_string):
    """
    Solve a Rubik's Cube using Kociemba's algorithm.

    Args:
        state_string (str): 54-char cube representation.

    Returns:
        list[str]: Move sequence as a list (e.g., ["R", "U'", "F2"])
    """
    # Validate first
    ok, error = validate_state(state_string)
    if not ok:
        raise ValueError(error)

    try:
        solution_str = kociemba.solve(state_string)
        steps = solution_str.split()
        return steps
    except Exception as e:
        raise ValueError(f"Solver error: {e}")


# ---- Manual test ----
if __name__ == "__main__":
    # Example: solved cube
    cube = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    print("Steps:", solve_cube(cube))
