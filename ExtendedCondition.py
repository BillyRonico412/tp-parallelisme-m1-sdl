from multiprocessing import Condition, Lock, Value


class ExtendedCondition:
    def __init__(self, lock: Lock):
        self.mutex = lock
        self.c_priorite: Condition = Condition(self.mutex)
        self.c_normal: Condition = Condition(self.mutex)
        self.nbre_priorite: Value = Value('i', 0)
        self.nbre_normal: Value = Value('i', 0)

    def wait(self, prio: int = 1):
        if prio == 0:
            self.nbre_priorite.value += 1
            self.c_priorite.wait()
            self.nbre_priorite.value -= 1
        else:
            self.nbre_normal.value += 1
            self.c_normal.wait()
            self.nbre_normal.value -= 1

    def empty(self) -> bool:
        return (self.nbre_priorite.value + self.nbre_normal.value) == 0

    def notify(self):
        if self.nbre_priorite.value > 0:
            self.c_priorite.notify()
        else:
            self.c_normal.notify()
