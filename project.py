import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

#config
RADIUS = 32
HOVER_RADIUS_INCREMENT = 8
FPS_DEFAULT = 30

FONT_PATH = "font/GothicA1-Medium.ttf"

LABEL_OFFSET_X = 18
LABEL_OFFSET_Y = -26

EXPLORE_W = 200
EXPLORE_H = 60
EXPLORE_MARGIN_BOTTOM = 90

COLOR_BG = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_CITY = (255, 255, 255)
COLOR_BTN_BG = (255, 255, 255)
COLOR_BTN_TEXT = (0, 0, 0)

FONT = cv2.FONT_HERSHEY_SIMPLEX

def draw_text(img, text, pos, font_size, color):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text(pos, font=font, text=text, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def measure_text(text, font_size):
    font = ImageFont.truetype(FONT_PATH, font_size)
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def overlay_image(bg, fg, x, y):
    height, width = fg.shape[:2]
    if fg.shape[2] == 3:
        bg[y:y+height, x:x+width] = fg
        return bg
    b, g, r, a = cv2.split(fg)
    alpha = a.astype(float) / 255
    alpha = cv2.merge([alpha]*3)
    roi = bg[y:y+height, x:x+width].astype(float)
    fg_rgb = cv2.merge((b, g, r)).astype(float)
    bg[y:y+height, x:x+width] = (fg_rgb * alpha + roi * (1 - alpha)).astype(np.uint8)
    return bg

def draw_label(frame, text, pos, color, font_scale=1.5):
    (tw, th), _ = cv2.getTextSize(text, FONT, font_scale, 2)
    x, y = pos
    y_top = y - th - 12
    if y_top < 0:
        y_top = y + th + 12
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y_top), (x + tw + 70, y_top + th + 10), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    cv2.putText(frame, text, (x + 7, y_top + th + 2), FONT, font_scale, color, 6, cv2.LINE_AA)
    return frame

def draw_city_label(display, name, px, py, hovering, color):
    if not hovering:
        return display
    end_x, end_y = px + 120, py - 60
    cv2.line(display, (px, py), (end_x, end_y), color, 2, cv2.LINE_AA)
    return draw_text(display, name, (end_x + LABEL_OFFSET_X, end_y + LABEL_OFFSET_Y), 34, color)

map_img = cv2.imread("japan-map.png", cv2.IMREAD_UNCHANGED)
MAP_HEIGHT, MAP_WIDTH = map_img.shape[:2]

cv2.namedWindow("Map", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Map", MAP_WIDTH, MAP_HEIGHT)

#config
click_points = {
    "TOKYO":   (1175, 1300),
    "KYOTO":   (720, 1400),
    "OSAKA":   (750, 1460),
    "NAHA": (80, 1915),
    "FUKUOKA": (250, 1550),
    "SAPPORO": (1310, 340),
    "SENDAI":  (1275, 1010),
}

CITY_FILTERS = {
    "5AM": ["TOKYO", "KYOTO", "OSAKA", "NAHA", "FUKUOKA"],
    "8PM": ["TOKYO", "SAPPORO", "SENDAI"]
}

#video
CITY_VIDEOS = {
    "TOKYO": {"day": "result/tokyo.mp4", "night": "result/tokyo2.mp4"},
    "KYOTO": "result/kyoto.mp4",
    "OSAKA": "result/osaka.mp4",
    "NAHA": "result/naha.mp4",
    "FUKUOKA": "result/fukuoka.mp4",
    "SAPPORO": "result/sapporo.mp4",
    "SENDAI": "result/sendai.mp4",
}

card_images = {}

time_state = "5AM"
current_city = None
current_video = None
mouse_x, mouse_y = 0, 0

button_coords = (70, 420)
button_size = (160, 60)

REF_BTN_PADDING_X = 20
REF_BTN_PADDING_Y = 10
REF_BTN_SIZE = (180, 60)
REF_BTN_MARGIN = 20
ref_button_coords = (MAP_WIDTH - REF_BTN_SIZE[0] - REF_BTN_MARGIN, MAP_HEIGHT - REF_BTN_SIZE[1] - REF_BTN_MARGIN)
REF_BTN_RECT = (0,0,0,0)

def draw_toggle(display):
    btn_x, btn_y = button_coords
    btn_w, btn_h = button_size
    tw, th = measure_text(time_state, 32)
    tx = btn_x + (btn_w - tw) // 2
    ty = btn_y + (btn_h - th) // 2
    cv2.rectangle(display, (btn_x, btn_y), (btn_x+btn_w, btn_y+btn_h), COLOR_BTN_BG, -1)
    return draw_text(display, time_state, (tx, ty), 30, COLOR_BTN_TEXT)

def show_references_window():
    ref_img = cv2.imread("references.png", cv2.IMREAD_UNCHANGED)
    if ref_img is None:
        print("references.png introuvable")
        return
    h, w = ref_img.shape[:2]
    x_pos = (MAP_WIDTH - w) // 2
    y_pos = (MAP_HEIGHT - h) // 2
    running = True
    while running:
        display = np.zeros((MAP_HEIGHT, MAP_WIDTH, 3), dtype=np.uint8)
        display = overlay_image(display, map_img, 0, 0)
        display = overlay_image(display, ref_img, x_pos, y_pos)
        cv2.imshow("Map", display)
        key = cv2.waitKey(30) & 0xFF
        if key in [27, ord("q")]:
            running = False

def draw_map_ui():
    global REF_BTN_RECT
    display = overlay_image(np.zeros((MAP_HEIGHT, MAP_WIDTH, 3), dtype=np.uint8), map_img, 0, 0)

    for name in CITY_FILTERS[time_state]:
        px, py = click_points[name]
        hovering = (mouse_x - px)**2 + (mouse_y - py)**2 <= RADIUS**2
        radius = RADIUS + (HOVER_RADIUS_INCREMENT if hovering else 0)
        cv2.circle(display, (px, py), radius, COLOR_CITY, 3 if hovering else 2)
        cv2.circle(display, (px, py), 4, COLOR_CITY, -1)
        display = draw_city_label(display, name, px, py, hovering, COLOR_CITY)

    display = draw_toggle(display)

    margin_x = button_coords[0]
    current_y = 120

    title_text = "They never sleep"
    display = draw_text(display, title_text, (margin_x, current_y), 36, COLOR_TEXT)
    _, th = measure_text(title_text, 36)
    current_y += th + 40

    para_text = (
        "Explore Japan's cities day and night.\n"
        "Discover the hidden rhythm of work.\n"
        "Press the time button to switch.\n"
        "Press 'Q' to close a video.\n"
        "Press 'Escape' to exit the app."
    )
    for line in textwrap.wrap(para_text, width=46):
        display = draw_text(display, line, (margin_x, current_y), 30, COLOR_TEXT)
        _, lh = measure_text(line, 24)
        current_y += lh + 16

    if current_city:
        state = "day" if time_state == "5AM" else "night"
        card_images.setdefault(current_city, {})
        if state not in card_images[current_city]:
            card_images[current_city][state] = cv2.imread(f"cards/{current_city.capitalize()}-card-{state}.png", cv2.IMREAD_UNCHANGED)
        card = card_images[current_city][state]
        card_height, card_width = card.shape[:2]
        card_x = (MAP_WIDTH - card_width) // 2
        card_y = (MAP_HEIGHT - card_height) // 2
        display = overlay_image(display, card, card_x, card_y)
        ex1 = card_x + (card_width - EXPLORE_W)//2
        ex2 = card_x + (card_width + EXPLORE_W)//2
        ey2 = card_y + card_height - EXPLORE_MARGIN_BOTTOM
        ey1 = ey2 - EXPLORE_H

    ref_x, ref_y = ref_button_coords
    ref_x -= 20
    tw, th = measure_text("References", 32)
    display = draw_text(display, "References", (ref_x, ref_y), 32, COLOR_TEXT)
    REF_BTN_RECT = (ref_x - 20, ref_y - 10, ref_x + tw + 20, ref_y + th + 10)

    return display

def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or FPS_DEFAULT
    cv2.namedWindow("Explore", cv2.WINDOW_NORMAL)
    running = True
    while running:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Explore", frame)
        if cv2.waitKey(int(1000 / fps)) & 0xFF in [27, ord("q")]:
            running = False
    cap.release()
    cv2.destroyWindow("Explore")

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y, time_state, current_city, current_video
    mouse_x, mouse_y = x, y
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    btn_x, btn_y = button_coords
    btn_w, btn_h = button_size
    if btn_x <= x <= btn_x+btn_w and btn_y <= y <= btn_y+btn_h:
        time_state = "8PM" if time_state == "5AM" else "5AM"
        current_city = None
        return

    rx1, ry1, rx2, ry2 = REF_BTN_RECT
    if rx1 <= x <= rx2 and ry1 <= y <= ry2:
        show_references_window()
        return

    if current_city:
        state = "day" if time_state == "5AM" else "night"
        card = card_images[current_city][state]
        card_height, card_width = card.shape[:2]
        card_x = (MAP_WIDTH - card_width)//2
        card_y = (MAP_HEIGHT - card_height)//2
        ex1 = card_x + (card_width - EXPLORE_W)//2
        ex2 = card_x + (card_width + EXPLORE_W)//2
        ey2 = card_y + card_height - EXPLORE_MARGIN_BOTTOM
        ey1 = ey2 - EXPLORE_H
        if ex1 <= x <= ex2 and ey1 <= y <= ey2:
            current_video = CITY_VIDEOS["TOKYO"][state] if current_city == "TOKYO" else CITY_VIDEOS[current_city]
            return
        if not (card_x <= x <= card_x+card_width and card_y <= y <= card_y+card_height):
            current_city = None
            return

    for name in CITY_FILTERS[time_state]:
        px, py = click_points[name]
        if (x - px)**2 + (y - py)**2 <= RADIUS**2:
            current_city = name
            return

cv2.setMouseCallback("Map", mouse_callback)

running = True
while running:
    cv2.imshow("Map", draw_map_ui())
    if current_video:
        play_video(current_video)
        current_video = None
    if cv2.waitKey(30) & 0xFF == 27:
        running = False

cv2.destroyAllWindows()