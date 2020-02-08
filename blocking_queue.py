from threading import Condition, Thread, current_thread
import random
import time


class BlockingQueue:
    def __init__(self, max_size):
        self.max_size = int(max_size)
        self.curr_size = 0
        self.queue = []
        self.cond = Condition()

    def enqueue(self, item):
        self.cond.acquire()
        while self.curr_size >= self.max_size:
            self.cond.wait()

        self.queue.append(item)
        self.curr_size += 1
        self.cond.notify_all()
        self.cond.release()

    def dequeue(self):
        self.cond.acquire()
        while self.curr_size == 0:
            self.cond.wait()

        item = self.queue.pop(0)
        self.curr_size -= 1
        self.cond.notify_all()
        self.cond.release()
        return item

    @property
    def is_full(self):
        return self.curr_size >= self.max_size


def consumer_thread(queue):
    while True:
        item = queue.dequeue()
        print(f"[{current_thread().getName()}@{time.strftime('%T')}] dequeued {item}")
        time.sleep(random.randint(2, 4))


def producer_thread(queue):
    while (item := random.choice(["🍉", "🍒", "🥭", "🍎", "🍏"])) :
        queue.enqueue(item)
        print(f"[{current_thread().getName()}@{time.strftime('%T')}] enqueued {item}")
        time.sleep(random.randint(1, 2))


def queue_monitor(queue):
    while True:
        if queue.is_full:
            print(f"[{current_thread().getName()}@{time.strftime('%T')}] queue is full")
        time.sleep(0.5)


def main():
    queue = BlockingQueue(5)
    Thread(
        name="Consumer-1", target=consumer_thread, args=(queue,), daemon=True
    ).start()
    Thread(
        name="Consumer-2", target=consumer_thread, args=(queue,), daemon=True
    ).start()
    Thread(
        name="Producer-1", target=producer_thread, args=(queue,), daemon=True
    ).start()
    Thread(
        name="Producer-2", target=producer_thread, args=(queue,), daemon=True
    ).start()
    Thread(
        name="QMonitor-1", target=queue_monitor, args=(queue,), daemon=True
    ).start()

    time.sleep(30)


if __name__ == "__main__":
    main()
