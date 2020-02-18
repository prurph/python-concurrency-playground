import random
import time
from collections import namedtuple
from enum import Enum
from threading import Condition, Semaphore, Thread


class Side(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    EMPTY = "EMPTY"


Baboon = namedtuple("baboon", ["name"])


class UnfairBaboonsCrossing:
    """
        There are baboons on the left and right side of a canyon with a vine separating them.
        Allow baboons to only cross in one direction (but many can cross concurrently) at a time.
        Is "unfair" in that it will starve baboons (threads) on one side of the canyon if there
        is an infinite stream of them coming from the other side.
    """

    def __init__(self, max_vine_cap):
        self.max_vine_cap = max_vine_cap
        self.side = Side.EMPTY
        self.curr_baboons = Semaphore(max_vine_cap)
        self.cv = Condition()

    def report_crossing(self, baboon):
        print(f"🐒 {baboon.name} is crossing to the {self.side}")
        time.sleep(1)

    def cross(self, baboon, side):
        with self.cv:
            while self.side is not Side.EMPTY and self.side is not side:
                self.cv.wait()
            self.curr_baboons.acquire()
            self.side = side

        # No synchronization needed here: we are guaranteed we have
        # set our side, and we have a permit from the semaphore
        self.report_crossing(baboon)
        self.curr_baboons.release()

        # We're done crossing, update the side if required
        with self.cv:
            if self.current_crossing_count == 0:
                self.side = Side.EMPTY
            self.cv.notify_all()

    @property
    def current_crossing_count(self):
        return self.max_vine_cap - self.curr_baboons._value

BABOONS = list(
    map(
        Baboon,
        [
            "Coco",
            "Frances",
            "Floyd",
            "Bananas",
            "Jo-jo",
            "Mr. Babson, Esq.",
            "Fluff",
            "Sally",
            "Rocco",
        ],
    )
)

def test_backup():
    # Since this is the "unfair" solution, expect to see
    # the one baboon trying to go left wait until the very end
    ubc = UnfairBaboonsCrossing(2)
    going_right = [
        Thread(target=ubc.cross, args=(x, Side.RIGHT))
        for x in BABOONS
    ]
    lefty = Thread(target=ubc.cross, args=(Baboon("Lefty"), Side.LEFT))
    for thread in going_right[:3]:
        thread.start()
    lefty.start()
    for thread in going_right[3:]:
        thread.start()

    for thread in (*going_right, lefty):
        thread.join()

def main():
    ubc = UnfairBaboonsCrossing(3)
    threads = [
        Thread(target=ubc.cross, args=(x, random.choice([Side.LEFT, Side.RIGHT])))
        for x in BABOONS
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
