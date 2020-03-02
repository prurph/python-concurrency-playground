import random
import time
from abc import ABC, abstractmethod
from threading import Semaphore, Thread, current_thread


class DiningPhilosophers(ABC):
    def philosophize(self, philosopher_id):
        while not self.exit:
            self.contemplate()
            self.attempt_eat(philosopher_id)

    def contemplate(self):
        print(f"{current_thread().getName():<12} is contemplating 🧠🤔🤓🧐😑")
        time.sleep(random.random() * 3 + 1)

    def eat(self):
        print(f"{current_thread().getName():<12} is eating        🍉🌮🍕🍦🥗")
        time.sleep(random.random() * 3 + 1)

    @abstractmethod
    def attempt_eat(self, philosopher_id):
        pass


class DiningPhilosophersEatingSemaphore(DiningPhilosophers):
    """Solution to dining philosophers problem that relies on an extra semaphore."""

    def __init__(self):
        self.forks = [Semaphore(1) for _ in range(5)]
        self.eating = Semaphore(4)
        self.exit = False

    def attempt_eat(self, philosopher_id):
        # Order matters: get eating semaphore first
        sems = [self.eating, self.forks[philosopher_id], self.forks[philosopher_id - 1]]
        for sem in sems:
            sem.acquire()
        self.eat()
        for sem in sems:
            sem.release()


class DiningPhilosophersLeftHanded(DiningPhilosophers):
    """Solution to dining philosophers problem that relies on a single left-hander."""

    def __init__(self):
        self.forks = [Semaphore(1) for _ in range(5)]
        self.exit = False
        self.left_hander = random.randrange(0, len(self.forks))

    def attempt_eat(self, philosopher_id):
        left_fork, right_fork = (
            self.forks[philosopher_id],
            self.forks[philosopher_id - 1],
        )
        sems = (
            [left_fork, right_fork]
            if philosopher_id == self.left_hander
            else [right_fork, left_fork]
        )
        for sem in sems:
            sem.acquire()
        self.eat()
        for sem in sems:
            sem.release()


PHILOSOPHERS = [
    "Aristotle",
    "Descartes",
    "Kant",
    "Kierkegaard",
    "Locke",
    "Nietzsche",
    "Plato",
    "Socrates",
    "Voltaire",
]


def test_problem(problem):
    print(f"\n*** Testing {problem.__class__.__name__} ***\n")
    random.shuffle(PHILOSOPHERS)
    threads = [
        Thread(name=philosopher, target=problem.philosophize, args=(i,))
        for i, philosopher in enumerate(PHILOSOPHERS[:5])
    ]
    for thread in threads:
        thread.start()

    time.sleep(20)
    problem.exit = True

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    test_problem(DiningPhilosophersEatingSemaphore())
    test_problem(DiningPhilosophersLeftHanded())
