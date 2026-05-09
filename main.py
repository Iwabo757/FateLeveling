import customtkinter as ctk
import pytesseract
import cv2
import numpy as np
import mss
import pyautogui
import time
from PIL import Image

# CHANGE THIS IF YOUR TESSERACT PATH IS DIFFERENT
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# SCREEN REGION OF TEAM WINDOW
# Adjust later if needed
ROSTER_REGION = {
    "top": 150,
    "left": 0,
    "width": 500,
    "height": 900
}

def capture_roster():
    with mss.mss() as sct:
        screenshot = sct.grab(ROSTER_REGION)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(gray, None, fx=2, fy=2)

    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh
import pyautogui
import time

def scan_roster():
    textbox.delete("1.0", "end")

    all_text = ""

    # CLICK INSIDE TEAM WINDOW FIRST
    pyautogui.click(250, 300)

    time.sleep(1)

    previous_text = ""

    for i in range(30):

        img = capture_roster()

        processed = preprocess(img)

        text = pytesseract.image_to_string(
            processed,
            config="--psm 6"
        )

        all_text += "\n" + text

        textbox.delete("1.0", "end")
        textbox.insert("end", all_text)

        # STOP IF SCROLL REPEATS
        if text == previous_text:
            break

        previous_text = text

        # SCROLL DOWN
        pyautogui.scroll(-700)

        time.sleep(1)

    cv2.imwrite("debug_capture.png", processed)

app = ctk.CTk()

app.geometry("700x600")
app.title("PokeMMO Team Scanner")

title = ctk.CTkLabel(
    app,
    text="Team Roster OCR",
    font=("Arial", 28, "bold")
)
title.pack(pady=20)

scan_button = ctk.CTkButton(
    app,
    text="Scan Team",
    command=scan_roster,
    width=250,
    height=50
)
scan_button.pack(pady=10)

textbox = ctk.CTkTextbox(
    app,
    width=600,
    height=400,
    font=("Consolas", 16)
)
textbox.pack(pady=20)

app.mainloop()