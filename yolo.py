import os
import cv2
from ultralytics import YOLO

COLOR_TEXT = (240, 240, 240)
BOX_COLOR = (220, 220, 220)
FONT = cv2.FONT_HERSHEY_SIMPLEX

#config
CLASS_COLORS = {
    "person": (255, 255, 255),
    "backpack": (180, 180, 180),
    "handbag": (150, 200, 220),
    "bicycle": (240, 240, 180),
}

def draw_box(frame, x1, y1, x2, y2, label, conf):
    color = CLASS_COLORS.get(label.lower(), BOX_COLOR)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label_text = f"{label}  {int(conf * 100)}%"
    (tw, th), _ = cv2.getTextSize(label_text, FONT, 1.25, 2)
    label_bg_top = y1 - th - 12
    if label_bg_top < 0:
        label_bg_top = y1 + th + 12
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x1, label_bg_top),
        (x1 + tw + 70, label_bg_top + th + 10),
        (0, 0, 0),
        -1
    )
    frame = cv2.addWeighted(overlay, 0.60, frame, 0.4, 0)
    cv2.putText(
        frame, label_text,
        (x1 + 7, label_bg_top + th + 2),
        FONT, 1.5, color, 6, cv2.LINE_AA
    )
    return frame

def draw_hud(frame, counts):
    hud_x, hud_y = 100, 220
    cv2.putText(frame, "DETECTIONS", (hud_x, hud_y), FONT, 2, COLOR_TEXT, 6, cv2.LINE_AA)
    offset = 70
    for obj, n in counts.items():
        obj_text = f"{obj.capitalize()}  {n:02d}"
        cv2.putText(frame, obj_text, (hud_x, hud_y + offset), FONT, 1.8, COLOR_TEXT, 5, cv2.LINE_AA)
        offset += 60
    return frame

model = YOLO("yolov8s.pt")

#class
objects_of_interest = ["person"]

#path
video_path = "../video/fukuoka.mp4"
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

file_name = os.path.splitext(os.path.basename(video_path))[0]

os.makedirs("result", exist_ok=True)
output_video_path = f"result/{file_name}.mp4"

out = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break
    try:
        results = model.predict(frame, conf=0.5, iou=0.7, imgsz=832)
    except Exception as e:
        print("YOLO Error:", e)
        continue
    counts = {obj: 0 for obj in objects_of_interest}
    if results:
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls].lower()
                conf = float(box.conf[0])
                if label in counts:
                    counts[label] += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                frame = draw_box(frame, x1, y1, x2, y2, label, conf)
    frame = draw_hud(frame, counts)
    out.write(frame)
    cv2.imshow("AI Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()