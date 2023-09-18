import time

class Time_Tool:
    def __init__(self, name='time_tool'):
        self.name = name
        self._start_time = time.time()
        self._end_time = None

    def format_duration(self, duration):
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return f"{hours}h {minutes}min {seconds}sec"

    def start_timer(self):
        start_time = time.time()
        self._start_time = start_time

    def end_timer(self):
        end_time = time.time()
        self._end_time = end_time
        msg = self.format_duration(self._end_time - self._start_time)
        return msg