import os
from tkinter import messagebox

from pynput import mouse, keyboard
from datetime import datetime

from program_using_logger.logger import get_logger
base_dir = f'{'\\'.join(__file__.split('\\')[:-1])}'
LOGGER = get_logger(os.path.join(base_dir, 'last.log'))

from program_using_logger.window_logger import WindowLogger
from program_using_logger.window_handler import *

path_to_csv = os.path.join(base_dir , 'logs', datetime.now().strftime("%m_%Y"), 
        f'{datetime.now().strftime("%d_%m_%Y")}.csv')

def check_csv_path(path:str):
    dir_list = os.path.normpath(path).split(os.sep)[:-1]
    current_path = ''
    for dir in dir_list:
        current_path += f'{dir}\\'
        if not os.path.exists(current_path):
            os.mkdir(current_path)

    if os.path.exists(path): return

    with open(path, 'w') as file:
        file.write(','.join(['name', 'time'])+'\n')

check_csv_path(path_to_csv)

update_time = 5

window_logger = WindowLogger(path_to_csv, 60*update_time)

last_time_moved = time.perf_counter()
def on_move(*_):
    global last_time_moved
    last_time_moved = time.perf_counter()

mouse_listener = mouse.Listener(
    on_move=on_move)
mouse_listener.daemon = True
mouse_listener.start()

keyboard_listener = keyboard.Listener(
    on_press=on_move)
keyboard_listener.daemon = True
keyboard_listener.start()

time_in_front = 0
try:
    while True:
        executable = get_active_window_name()
        if time.perf_counter()-last_time_moved > 60*update_time/2:
            executable = 'AFK'
            time_in_front = max(0, time_in_front-update_time)
        else:
            time_in_front += update_time
        LOGGER.debug(f"Current executable: {executable}")
        window_logger.change_executable(executable)
        
        time.sleep(update_time)

        if time_in_front > 120*60:
            LOGGER.info(f"Sitting already {round(time_in_front/60)} minutes")
            messagebox.showinfo("Time to take a stretch",
                                f"You are sitting already {round(time_in_front/60)} minutes")
            time_in_front = 0
except Exception as e:
    LOGGER.critical(e)
finally:
    window_logger.emergeny_write()