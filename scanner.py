# scanner.py
import cv2
import numpy as np
import json

# =========================
# 1. HSV COLOR RANGES
# =========================

# Adjust according to your cube
COLOR_RANGES = {
    "R": ((0, 80, 80), (10, 255, 255)),      # red
    "O": ((10, 80, 80), (20, 255, 255)),     # orange
    "Y": ((20, 80, 80), (35, 255, 255)),     # yellow
    "G": ((40, 60, 50), (75, 255, 255)),     # green
    "B": ((90, 60, 60), (130, 255, 255)),    # blue
    "W": ((0, 0, 180), (180, 50, 255)),      # white
}

# =========================
# 2. Color classifier
# =========================
def detect_color(hsv_pixel):
    h, s, v = hsv_pixel
    for label, (lower, upper) in COLOR_RANGES.items():
        lower = np.array(lower)
        upper = np.array(upper)
        if np.all(h >= lower) and np.all(h <= upper):
            return label
    return "?"

# =========================
# 3. Largest contour → Face crop
# =========================
def extract_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edge = cv2.Canny(blur, 40, 120)

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    cnt = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(cnt, 0.05 * cv2.arcLength(cnt, True), True)

    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        return frame[y:y+h, x:x+w]

    return None

# =========================
# 4. 3×3 Grid → 9 colors
# =========================
def read_grid(face_img):
    hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
    h, w = hsv.shape[:2]
    cell_h = h // 3
    cell_w = w // 3

    colors = []
    for r in range(3):
        for c in range(3):
            cy = r * cell_h + cell_h // 2
            cx = c * cell_w + cell_w // 2
            pixel = hsv[cy, cx]
            colors.append(detect_color(pixel))

    return colors

# =========================
# 5. Scan flow
# =========================
def scan_cube():
    cam = cv2.VideoCapture(0)
    faces = {}

    face_order = ["U", "R", "F", "D", "L", "B"]
    idx = 0

    print("▶️ Camera open")
    print("Place cube face in center → Press SPACE to capture")
    print("ESC = exit anytime")

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        cv2.putText(frame, f"Face: {face_order[idx]}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (255, 255, 255), 2)

        face = extract_face(frame)
        if face is not None:
            cv2.rectangle(frame, (10,10), (150,60), (0,255,0), 2)
            preview = cv2.resize(face, (300, 300))
            cv2.imshow("Detected Face", preview)

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

        if key == 32 and face is not None:  # SPACE
            colors = read_grid(face)
            faces[face_order[idx]] = colors
            print(f"✔️ Captured {face_order[idx]}:", colors)

            idx += 1
            if idx == len(face_order):
                print("🎉 All faces captured")
                break

    cam.release()
    cv2.destroyAllWindows()
    return faces


# =========================
# 6. Save JSON
# =========================
if __name__ == "__main__":
    faces = scan_cube()
    with open("cube_state.json", "w") as f:
        json.dump(faces, f, indent=2)
    print("📦 Saved -> cube_state.json")
