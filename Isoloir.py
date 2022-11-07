import sys
import time
import random

from multiprocessing import Process, Lock, Value
from ExtendedCondition import ExtendedCondition as Cond

class Isoloir:
    def __init__(self, nbre_isoloir: int):

        self.mutex: Lock = Lock()

        # Notre condition
        self.cond: Cond = Cond(self.mutex)

        # Nbre d'isoloir vide
        self.nb_isoloir_vide: Value = Value('i', nbre_isoloir)

    def start_vote(self, priorite: bool):
        with self.mutex:
            while self.nb_isoloir_vide.value == 0:
                if priorite:
                    self.cond.wait(0)
                else:
                    self.cond.wait()
            self.nb_isoloir_vide.value -= 1
            self.cond.notify()

    def end_vote(self):
        with self.mutex:
            self.nb_isoloir_vide.value += 1
            self.cond.notify()


def vote(synchro: Isoloir, id_electeur: int, priorite: bool = False):
    print("%s %s veut voter" % ("P: " if priorite else "N: ", id_electeur))
    synchro.start_vote(priorite)
    print("%s %s est entrain de voter" % ("P: " if priorite else "N: ", id_electeur))
    time.sleep(.5 + random.random())
    synchro.end_vote()
    print("%s %s a fini de voter" % ("P: " if priorite else "N: ", id_electeur))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: %s <Nb isoloir> <Nb electeur normal> <Nb electeur priorité> \n" % sys.argv[0])

    nb_isoloir: int = int(sys.argv[1])
    nb_electeur_normal: int = int(sys.argv[2])
    nb_electeur_priorite: int = int(sys.argv[3])

    synchro: Isoloir = Isoloir(nb_isoloir)

    processes = []

    for id_electeur_normal in range(nb_electeur_normal):
        electeur_normal = Process(target=vote, args=(synchro, id_electeur_normal))
        electeur_normal.start()
        processes.append(electeur_normal)

    for id_electeur_priorite in range(nb_electeur_priorite):
        electeur_priorite = Process(target=vote, args=(synchro, id_electeur_priorite, True))
        electeur_priorite.start()
        processes.append(electeur_priorite)

    for process in processes:
        process.join()
