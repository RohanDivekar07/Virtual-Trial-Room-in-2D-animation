import cv2
import imutils
import numpy as np
import ChangeClothes as cc
import random
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Canvas, Label

# Global variables
cap = cv2.VideoCapture(0)
images = cc.loadImages()
thres = [130, 40, 75, 130]
curClothId = 1

def process_frame(cam, t_shirt, th):
    resized = imutils.resize(cam, width=800)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
    size = 180
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if r > 30:
                cv2.circle(cam, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(cam, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                size = r * 7

    size = min(max(size, 100), 350)
    t_shirt = imutils.resize(t_shirt, width=size)
    f_height, f_width = cam.shape[:2]
    t_height, t_width = t_shirt.shape[:2]
    height = int(f_height / 2 - t_height / 2)
    width = int(f_width / 2 - t_width / 2)
    roi = cam[height:height + t_height, width:width + t_width]
    t_shirt_gray = cv2.cvtColor(t_shirt, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(t_shirt_gray, th, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)
    img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    img_fg = cv2.bitwise_and(t_shirt, t_shirt, mask=mask)
    t_shirt = cv2.add(img_bg, img_fg)
    cam[height:height + t_height, width:width + t_width] = t_shirt

    return cam

def update_frame():
    global cap, canvas, photo, curClothId, thres, images
    ret, cam = cap.read()
    if not ret:
        window.after(10, update_frame)
        return
    cam = cv2.flip(cam, 1, 0)
    t_shirt = images[curClothId]
    th = thres[curClothId]
    cam = process_frame(cam, t_shirt, th)
    
    cv2image = cv2.cvtColor(cam, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.create_image(0, 0, anchor="nw", image=imgtk)
    window.after(10, update_frame)

def change_item(direction):
    global curClothId, images, thres
    new_id = curClothId + direction
    if 0 <= new_id < len(images) and new_id < len(thres):
        curClothId = new_id
    else:
        print("Index out of range: Attempt to access index", new_id, "of", len(images), "or", len(thres))

def take_snapshot():
    global cap
    rand = random.randint(1, 999999)
    cv2.imwrite('output/'+str(rand)+'.png', cap)

# Setup tkinter
window = tk.Tk()
window.title("Virtual Dressing Room")

# Define colors and styles
bg_color = "#333333"  # Dark background color
btn_color = "#4CAF50"  # Green color for buttons
text_color = "#FFFFFF"  # White color for text
canvas_color = "#FFFFFF"  # White background for the canvas
font_color = "#FFFFFF"  # White color for font
font_style = "Helvetica"  # Font style for the labels
font_size = 14  # Font size for the introduction text

# Apply colors and styles
window.configure(bg=bg_color)
welcome_text = Label(window, text="Welcome to the Virtual Trial Room", font=(font_style, 20, 'bold'), bg=bg_color, fg=font_color)
welcome_text.pack(pady=(10, 0))

introduction_text = Label(window, text="Try on different clothes without the hassle of physically changing!", font=(font_style, font_size), bg=bg_color, fg=font_color)
introduction_text.pack(pady=(0, 20))

canvas = Canvas(window, width=800, height=600, bg=canvas_color)
canvas.pack()

# Styling buttons with colors and padding for better UI
btn_next = Button(window, text="Next", width=20, command=lambda: change_item(1), bg=btn_color, fg=text_color)
btn_next.pack(anchor='center', pady=10)

btn_prev = Button(window, text="Previous", width=20, command=lambda: change_item(-1), bg=btn_color, fg=text_color)
btn_prev.pack(anchor='center', pady=10)



# Start the video frame update process
update_frame()

# Start the Tkinter event loop
window.mainloop()


