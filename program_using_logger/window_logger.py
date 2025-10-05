from datetime import datetime
from dataclasses import dataclass
from .logger import get_logger
from .window_handler import *
from copy import deepcopy

LOGGER = get_logger()

@dataclass
class Window:
    executable: str
    start_datetime: datetime

class WindowLogger:
    def __init__(self, log_path:str|None=None, chunk_size:int=60):
        self.chunk_history: list[Window] = []
        self.chunk_start_time = time.time()

        self.last_chunk_window: Window | None = None
        self.chunk_size = chunk_size

        self.log_path = log_path

    def write_chunk(self):
        start_time = self.chunk_history[0].start_datetime
        end_time = datetime.now()

        last_window_datetime = deepcopy(start_time)
        chunk_durations = {}
        for window in self.chunk_history:
            duration = (window.start_datetime-last_window_datetime).microseconds
            if window.executable in chunk_durations.keys():
                chunk_durations[window.executable] += duration
            else:
                chunk_durations[window.executable] = duration
            last_window_datetime = window.start_datetime

        most_usable_executable = None
        max_duration = 0
        for index, chunk_duration in enumerate(chunk_durations.values()):
            if chunk_duration > max_duration:
                max_duration = chunk_duration
                most_usable_executable = tuple(chunk_durations.keys())[index]

        if self.last_chunk_window is None:
            self.last_chunk_window = Window(
                most_usable_executable, start_time
            )
            self._write_last_chunk()
        
        elif self.last_chunk_window.executable != most_usable_executable:
            self.last_chunk_window = Window(
                most_usable_executable, start_time
            )
            self._write_last_chunk()

        self.chunk_history.clear()

    def _write_last_chunk(self):
        LOGGER.info(f"Writing chunk {self.last_chunk_window}")
        if self.log_path is not None and self.last_chunk_window is not None:
            with open(self.log_path, 'a') as file:
                file.write(self.last_chunk_window.executable+
                           f",{self.last_chunk_window.start_datetime.strftime("%H:%M:%S")}\n")
                
    def emergeny_write(self):
        LOGGER.warning(f"Emergency write!")
        self._write_last_chunk()

        with open(self.log_path, 'a') as file:
            file.write("Emergency shutdown"+
                        f",{datetime.now().strftime("%H:%M:%S")}\n")

    def change_executable(self, executable:str):
        new_window = Window(executable,
                          datetime.now())
        
        self.chunk_history.append(new_window)
        
        if time.time()-self.chunk_start_time > self.chunk_size:
            self.write_chunk()
            self.chunk_start_time = time.time()
                
if __name__ == '__main__':
    logger = WindowLogger()
    while True:
        current_executable = get_active_window_name()
        logger.change_executable(current_executable)
        time.sleep(5)