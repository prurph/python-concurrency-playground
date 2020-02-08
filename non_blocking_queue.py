import random
import time
from collections import deque
from concurrent.futures import Future
from threading import RLock, Thread, current_thread


class NonBlockingQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = deque([])
        self.waiting_enq = deque([])
        self.waiting_deq = deque([])
        # Need RLock because future callbacks are executed in the
        # thread resolving them, so when caller attaches a callback
        # that retries their operation, it will execute in the thread
        # that already has the lock, and it will deadlock.
        self.lock = RLock()

    def dequeue(self):
        result = future = None
        with self.lock:
            if self.queue:
                result = self.queue.popleft()
                if self.waiting_enq:
                    self.waiting_enq.popleft().set_result(True)
            else:
                future = Future()
                self.waiting_deq.append(future)
        return result, future

    def enqueue(self, item):
        future = None
        with self.lock:
            if len(self.queue) >= self.max_size:
                future = Future()
                self.waiting_enq.append(future)
            else:
                self.queue.append(item)
                if self.waiting_deq:
                    self.waiting_deq.popleft().set_result(self.queue.popleft())
        return future

    def get_metrics(self):
        ac = len(self.queue) - self.max_size
        return {
            "avail_cap": self.max_size - len(self.queue),
            "waiting_puts": len(self.waiting_enq),
            "waiting_gets": len(self.waiting_deq),
        }


def retry_deq(future):
    print(
        f"[{current_thread().getName()}@{time.strftime('%T')}] executed retry_deq, dequeued: {future.result()}"
    )


def consumer_thread(queue, cadence_range):
    while True:
        item, future = queue.dequeue()
        if item is None:
            future.add_done_callback(retry_deq)
        else:
            print(
                f"[{current_thread().getName()}@{time.strftime('%T')}] dequeued: {item}"
            )
        time.sleep(random.choice(cadence_range))


def retry_enq(future):
    print(f"[{current_thread().getName()}@{time.strftime('%T')}] retry_enq invoked")
    item, queue = future.item, future.queue
    retry_fut = queue.enqueue(item)

    if retry_fut is not None:
        retry_fut.item = item
        retry_fut.queue = queue
        retry_fut.add_done_callback(retry_enq)
    else:
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] executed retry_enq: enqueued: {item}"
        )


def producer_thread(queue, cadence_range):
    while (item := random.choice(["🍉", "🍒", "🥭", "🍎", "🍏"])) :
        queue.enqueue(item)
        print(f"[{current_thread().getName()}@{time.strftime('%T')}] enqueued {item}")
        time.sleep(random.choice(cadence_range))


def queue_monitor(queue):
    while True:
        print(queue.get_metrics())
        time.sleep(1)


if __name__ == "__main__":
    queue = NonBlockingQueue(5)
    Thread(
        name="Consumer-1",
        target=consumer_thread,
        args=(queue, range(3, 4)),
        daemon=True,
    ).start()
    Thread(
        name="Producer-1",
        target=producer_thread,
        args=(queue, range(1, 2)),
        daemon=True,
    ).start()
    Thread(name="QMonitor-1", target=queue_monitor, args=(queue,), daemon=True).start()

    time.sleep(30)
