import time


class Timer:
    def __init__(self, name, print=True):
        self.name = name
        self.print = print

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        if self.print:
            print(f"  <timer> {self.name} took {self.elapsed_time:.4f} seconds")
