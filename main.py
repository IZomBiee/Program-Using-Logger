import time
import os
import psutil
import ctypes
import logging

from tkinter import messagebox
from pynput import mouse, keyboard
from datetime import datetime
from ctypes import wintypes

def add_new_record(name:str, time:str, duration:float):
    record_string = f'{name},{time},{duration}'
    logger.info(f"Added new record: {record_string}")
    with open(path_to_csv, 'a') as file:
        file.write(record_string+'\n')

def check_csv_path(path:str):
    dir_list = os.path.normpath(path).split(os.sep)[:-1]
    current_path = ''
    for dir in dir_list:
        current_path += f'{dir}\\'
        if not os.path.exists(current_path):
            os.mkdir(current_path)

    if os.path.exists(path): return

    with open(path, 'w') as file:
        file.write(','.join(['name', 'time', 'duration'])+'\n')
    
def get_active_window_name() -> str:
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    GetForegroundWindow = user32.GetForegroundWindow
    GetForegroundWindow.argtypes = ()
    GetForegroundWindow.restype = wintypes.HWND

    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    GetWindowThreadProcessId.restype = wintypes.DWORD

    hwnd = GetForegroundWindow()
    pid = wintypes.DWORD()

    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    while True:
        try:
            process = psutil.Process(pid.value)
            executable_path = process.exe()
            executable_name = executable_path.split('\\')[-1]
            break
        except psutil.AccessDenied:
            logger.warning("Access Denied!")
            time.sleep(0.3)

    return executable_name

def get_logger() -> logging.Logger:
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(os.path.join(path_to_project, 'last.log'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

last_time_moved = time.perf_counter()
def on_move(*args):
    global last_time_moved
    last_time_moved = time.perf_counter()

path_to_project = f'{'\\'.join(__file__.split('\\')[:-1])}'

logger = get_logger()

logger.info("Start of program.")

path_to_csv = os.path.join(path_to_project , 'logs', datetime.now().strftime("%m_%Y"), 
        f'{datetime.now().strftime("%d_%m_%Y")}.csv')

path_to_csv = os.path.join(path_to_project , 'test.csv')

logger.info(f"Path to csv: {path_to_csv}")

check_csv_path(path_to_csv)

last_executable = None
last_executable_found_datetime = datetime.now().strftime('%H:%M:%S')
last_executable_found_time = time.perf_counter()

mouse_listener = mouse.Listener(
    on_move=on_move)
logger.info("Starting mouse listener.")
mouse_listener.start()

keyboard_listener = keyboard.Listener(
    on_press=on_move)
logger.info("Starting keyboard listener.")
keyboard_listener.start()

try:
    while True:
        if time.perf_counter()-last_time_moved > 60:
            current_executable = 'AFK'
        else: current_executable = get_active_window_name()

        if last_executable is None:
            logger.info(f"First executable is {current_executable}")
            last_executable = current_executable

        elif last_executable != current_executable:
            logger.debug(f"Change of executable from {last_executable} to {current_executable}")
            duration = time.perf_counter() - last_executable_found_time

            logger.debug(f"Previous executable duration: {duration}")

            if duration > 20:
                add_new_record(last_executable, last_executable_found_datetime, round(duration))

            last_executable = current_executable
            last_executable_found_time = time.perf_counter()
            last_executable_found_datetime = datetime.now().strftime('%H:%M:%S')

        time.sleep(1)
finally:
    mouse_listener.stop()
    keyboard_listener.stop()