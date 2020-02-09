import heapq
import math
import random
import time
from threading import Condition, Thread, current_thread


class DeferredCallbackExecutor:
    def __init__(self):
        self.actions = []
        self.condition = Condition()
        self.sleep_for = 0

    def add_action(self, action):
        action.exec_at = time.time() + action.delay_ms // 1000
        self.condition.acquire()
        heapq.heappush(self.actions, action)
        self.condition.notify()
        self.condition.release()

    def start(self):
        while True:
            self.condition.acquire()
            while not self.actions:
                self.condition.wait()
            while self.actions:
                next_action = self.actions[0]
                sleep_time = next_action.exec_at - time.time()
                if sleep_time <= 0:
                    break
                self.condition.wait(timeout=sleep_time)
            action = heapq.heappop(self.actions)
            action.action(action)
            self.condition.release()


class DeferredAction:
    def __init__(self, action, name, delay_ms):
        self.action = action
        self.name = name
        self.delay_ms = delay_ms
        # Set when action is added to the executor
        self.exec_at = None

    def __lt__(self, other):
        return self.exec_at < other.exec_at


def shout_fruit(action):
    fruit = random.choice(["🍉", "🍒", "🥭", "🍎", "🍏"])
    delta = time.time() - action.exec_at
    print(
        f"{fruit}! I'm action {action.name}. Time delta between actual and expected execution: {delta}"
    )


def main():
    executor = DeferredCallbackExecutor()
    Thread(target=executor.start, daemon=True).start()

    for i, delay_s in enumerate(range(2, 10, 2), 1):
        executor.add_action(
            DeferredAction(shout_fruit, f"ShoutFruit-{i}", delay_s * 1000)
        )

    time.sleep(11)


if __name__ == "__main__":
    main()
