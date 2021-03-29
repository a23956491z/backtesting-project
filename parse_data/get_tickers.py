import csv
import re
import pyautogui
import time
import keyboard
from PIL import Image
batch_size = 3
pyautogui.FAILSAFE= False




ticker_list = []
with open('all_ticker_1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        ticker = row[0]
        extracted = re.search("\d+", ticker).group()
        # print(extracted)
        ticker_list.append(extracted)

bx, by = 444, 133
ticker_field = (bx, by)

choose_btn = (bx-151,by+31)
save_btn = (bx+51, by+387)

import sys

def get_mouse_position(max_period = 60, times=1000):

    delay_time = float(max_period) / times
    for i in range(times):
        currentMouseX, currentMouseY = pyautogui.position()

        im = pyautogui.screenshot()
        px = im.getpixel((currentMouseX, currentMouseY))

        time.sleep(delay_time)
        print(px, '|',currentMouseX, ',',currentMouseY)

        if keyboard.is_pressed('F12'):
            break

def left_click(position):
    pyautogui.click(x=position[0], y=position[1], clicks=2, button='left')



def run_add_ticker(tickers):

    try:
        for ticker in tickers:
            print(ticker)
            left_click(ticker_field)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.typewrite(ticker)
            left_click(choose_btn)
            if keyboard.is_pressed('F12'):
                break
    except KeyboardInterrupt:
        sys.exit()

# for i in range(0, len(ticker_list) , batch_size):
#     print(i, ticker_list[i : i+batch_size])
#
#



# get_mouse_position()

while not keyboard.is_pressed('F12'):
    if keyboard.is_pressed('F10'):
        run_add_ticker(ticker_list)
        break;
