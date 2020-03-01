import random
import time
from threading import Condition, Thread, current_thread

class Barrier:
    def __init__(self, size):
        self.size = size
        self.occupancy = 0
        self.releasing_count = 0
        self.cv = Condition()

    def arrived(self):
        with self.cv:
            # No new threads can enter if we're at capacity; this
            # is required to prevent race conditions when releasing
            while self.occupancy == self.size:
                print(f"{current_thread().getName()} at capacity (flushing). No entry allowed.")
                self.cv.wait()

            # Bump occupancy and wait if necessary until full
            self.occupancy += 1
            if self.occupancy == self.size:
                print(f"{current_thread().getName()} occupancy {self.occupancy}/{self.size}. Releasing.")
                self.releasing_count = self.size
            else:
                print(f"{current_thread().getName()} occupancy {self.occupancy}/{self.size}. Waiting.")
                while self.occupancy < self.size:
                    self.cv.wait()

            # Gates have been opened, this thread is leaving.
            self.releasing_count -= 1
            if self.releasing_count == 0:
                self.occupancy = 0

            print(f"{current_thread().getName()} released")
            self.cv.notify_all()

def arrive(barrier, times, cadence_s):
    for _ in range(times):
        time.sleep(cadence_s)
        print(f"{current_thread().getName()} reached the barrier.")
        barrier.arrived()

def main():
    barrier = Barrier(3)

    threads = [Thread(name=f"Thread-{i}", target=arrive, args=(barrier, 5, 0.5 * i ** 2)) for i in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
