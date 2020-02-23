import random
import time
from threading import Condition, Semaphore, Thread, current_thread


class AsyncExecutor:
    def execute(self, callback):
        Thread(name=f"AsyncExecutor-{id(self)}", target=self.work, args=(callback,)).start()

    def work(self, callback):
        time.sleep(random.randint(1, 5))
        callback()


class SyncExecutorSem(AsyncExecutor):
    def __init__(self):
        self.sem = Semaphore(0)

    def execute(self, callback):
        super().execute(callback)
        self.sem.acquire()
        print(f"[{current_thread().getName()}@{time.strftime('%T')}] finished executing.")

    def work(self, callback):
        super().work(callback)
        self.sem.release()


class SyncExecutorCV(AsyncExecutor):
    def __init__(self):
        self.cv = Condition()
        self.is_done = False

    def execute(self, callback):
        super().execute(callback)
        with self.cv:
            while not self.is_done:
                self.cv.wait()
            self.is_done = False
        print(f"[{current_thread().getName()}@{time.strftime('%T')}] finished executing.")

    def work(self, callback):
        super().work(callback)
        print(
            f"[{current_thread().getName()}@{time.strftime('%T')}] finished work; notifying."
        )
        with self.cv:
            self.cv.notify_all()
            self.is_done = True


def shout_fruit():
    fruit = random.choice(["🍉", "🍒", "🥭", "🍎", "🍏"])
    print(
        f"[{current_thread().getName()}@{time.strftime('%T')}] is shouting fruit! {fruit}! {fruit * 3}!!!"
    )


def test(executor):
    start = time.time()
    executor.execute(shout_fruit)
    print(
        f"[{current_thread().getName()}@{time.strftime('%T')}] was blocked for {time.time() - start:0.2f} seconds by {executor.__class__.__name__}"
    )


if __name__ == "__main__":
    test(AsyncExecutor())
    test(SyncExecutorSem())
    test(SyncExecutorCV())
