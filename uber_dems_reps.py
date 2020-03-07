import random
from enum import Enum
from threading import Barrier, Lock, Semaphore, Thread, current_thread


class Party(Enum):
    DEM = "Democrat"
    REP = "Republican"


class UberDemsReps:
    CAR_CAPACITY = 4

    def __init__(self):
        self.rides = 0
        self.waiting = {Party.DEM: 0, Party.REP: 0}
        self.sems = {Party.DEM: Semaphore(0), Party.REP: Semaphore(0)}
        self.lock = Lock()
        self.barrier = Barrier(UberDemsReps.CAR_CAPACITY)

    def seated(self, party):
        print(f"{f'[{current_thread().getName()}]':<15} {party.value} seated")

    def drive(self, parties):
        self.rides += 1
        emojis = map(lambda x: "🐘" if x is Party.REP else "🐴", parties)
        print(
            f"{f'[{current_thread().getName()}]':<15} Ride {self.rides} departing {''.join(emojis)}"
        )

    def seat(self, party):
        full_car = False
        other_party = Party.DEM if party == Party.REP else Party.REP
        self.lock.acquire()
        self.waiting[party] += 1

        # If we're ready to go, build our fellow passengers
        if self.waiting[party] == 4:
            full_car = [party] * 4
        elif self.waiting[party] >= 2 and self.waiting[other_party] >= 2:
            full_car = [party] * 2 + [other_party] * 2
        # Otherwise, wait
        else:
            self.lock.release()
            self.sems[party].acquire()

        # We're ready to go! This thread will effectively act as the leader, signalling
        # to everyone else to get into the car.
        if full_car:
            # Let our full_car know we're ready by releasing the appropriate sems
            for tripmate_party in full_car[1:]:
                self.sems[tripmate_party].release()

        # Wait for everyone to get in the car
        self.seated(party)
        self.barrier.wait()

        if full_car:
            # Adjust waiting counts, now considering the last person, and drive
            for p in full_car:
                self.waiting[p] -= 1
            self.drive(full_car)
            self.lock.release()


def main():
    ubr = UberDemsReps()

    # 10 dems, 10 reps means at least one mixed car
    riders = [
        Thread(name=f"{party.value}-{i}", target=ubr.seat, args=(party,))
        for i in range(1, 11)
        for party in Party
    ]
    random.shuffle(riders)
    for rider in riders:
        rider.start()
    for rider in riders:
        rider.join()


if __name__ == "__main__":
    main()
