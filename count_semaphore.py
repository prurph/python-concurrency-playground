import time
from threading import Condition, Thread


class CountSemaphore:
    def __init__(self, max_count):
        self.max_count = max_count
        self.given_out = 0
        self.cv = Condition()

    def release(self):
        pass

    def acquire(self):
        self.cv.acquire()
        while self.given_out >= self.max_count:
            self.cv.wait()

        self.given_out += 1
        self.cv.notify_all()
        self.cv.release()

    def release(self):
        self.cv.acquire()
        while self.given_out == 0:
            self.cv.wait()

        self.given_out -= 1
        self.cv.notify_all()
        self.cv.release()


def ping(sem):
    print(f"PING!")
    sem.release()
    time.sleep(2)
    print(f"PING AGAIN!")
    sem.release()
    time.sleep(2)
    print(f"PING AGAIN AGAIN!")
    sem.release()
    time.sleep(2)
    print(f"PING A FOURTH TIME!")
    sem.release()


def pong(sem):
    sem.acquire()
    print(f"PONG!")
    sem.acquire()
    print(f"PONG AGAIN!")
    sem.acquire()
    print(f"PONG AGAIN AGAIN!")
    sem.acquire()
    print(f"PONG A FOURTH TIME!")


def main():
    cs = CountSemaphore(1)
    cs.acquire()
    ping_t = Thread(target=ping, args=(cs,))
    pong_t = Thread(target=pong, args=(cs,))

    pong_t.start()
    time.sleep(1)
    ping_t.start()

    ping_t.join()
    pong_t.join()


if __name__ == "__main__":
    main()
