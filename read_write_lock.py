import random
import time
from threading import Condition, Thread, current_thread


class ReadWriteLock:
    def __init__(self):
        self.cv = Condition()
        self.write_in_progress = False
        self.readers = 0

    def acquire_read_lock(self):
        self.cv.acquire()
        while self.write_in_progress:
            self.cv.wait()
        self.readers += 1
        self.cv.release()

    def release_read_lock(self):
        self.cv.acquire()
        self.readers -= 1
        # Only need to notify potential writers if we're the last reader out
        if self.readers == 0:
            self.cv.notify_all()
        self.cv.release()

    def acquire_write_lock(self):
        self.cv.acquire()
        while self.write_in_progress or self.readers > 0:
            self.cv.wait()
        self.write_in_progress = True
        self.cv.release()

    def release_write_lock(self):
        self.cv.acquire()
        self.write_in_progress = False
        self.cv.notify_all()
        self.cv.release()

    @property
    def state(self):
        return {"readers": self.readers, "write_in_progress": self.write_in_progress}


def writer(lock):
    while True:
        lock.acquire_write_lock()
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] acquired write lock ({lock.state})"
        )
        time.sleep(random.randint(1, 5))
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] releasing write lock ({lock.state})"
        )
        lock.release_write_lock()
        time.sleep(1)


def reader(lock):
    while True:
        lock.acquire_read_lock()
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] acquired read lock ({lock.state})"
        )
        time.sleep(random.randint(1, 2))
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] releasing read lock ({lock.state})"
        )
        lock.release_read_lock()
        time.sleep(1)


def main():
    rw_lock = ReadWriteLock()
    writers = [
        Thread(name=f"Writer-{i}", target=writer, args=(rw_lock,), daemon=True)
        for i in range(3)
    ]
    readers = [
        Thread(name=f"Reader-{i}", target=reader, args=(rw_lock,), daemon=True)
        for i in range(5)
    ]
    threads = readers + writers
    for thread in threads:
        thread.start()
    time.sleep(30)


if __name__ == "__main__":
    main()
