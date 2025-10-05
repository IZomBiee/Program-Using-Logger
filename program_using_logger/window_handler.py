import psutil
import ctypes
import time

from ctypes import wintypes

def get_active_window_name() -> str:
    while True:
        try:
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

            process = psutil.Process(pid.value)
            executable_path = process.exe()
            executable_name = executable_path.split('\\')[-1]
            break
        except psutil.AccessDenied:
            time.sleep(0.3)

    return executable_name