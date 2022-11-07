import sys
import time
import random
from multiprocessing import Process, Value, Condition, Lock

class RW:

    def __init__(self):

        # On a besoin du booleen qui indique qu'on est en train d'écrire ou pas

        self.bool_write = Value('i', 0)  # 0: non ecriture, 1 ecriture

        # On a besoin du nombre de lecteur en cours de lecture

        self.nb_read_en_cours = Value('i', 0)

        # On a besoin du nombre de lecteur et de redacteur en attente

        self.nb_read_attente = Value('i', 0)
        self.nb_write_attente = Value('i', 0)

        # On a besoin d'un mutex
        self.mutex = Lock()

        # On a besoin du condition pour les lecteurs et redacteur

        self.c_read = Condition(self.mutex)
        self.c_write = Condition(self.mutex)

    def start_read(self):
        with self.mutex:
            self.nb_read_attente.value += 1
            while self.bool_write.value == 1 or self.nb_write_attente.value > 0:
                self.c_read.wait()
            self.nb_read_attente.value -= 1
            self.nb_read_en_cours.value += 1
            if self.nb_write_attente.value == 0:
                self.c_read.notify()

    def end_read(self):
        with self.mutex:
            self.nb_read_en_cours.value -= 1
            if self.nb_read_en_cours.value == 0:
                self.c_write.notify()

    def start_write(self):
        with self.mutex:
            self.nb_write_attente.value += 1
            while self.bool_write.value == 1 or self.nb_read_en_cours.value != 0:
                self.c_write.wait()
            self.nb_write_attente.value -= 1
            self.bool_write.value = 1


    def end_write(self):
        with self.mutex:
            self.bool_write.value = 0
            if self.nb_write_attente.value == 0:
                self.c_read.notify()
            else:
                self.c_write.notify()


def process_writer(identifier, synchro):
    synchro.start_write()
    for _ in range(5):
        with open('LectRed_shared', 'a') as file_id:
            txt = ' ' + str(identifier)
            file_id.write(txt)
            print('Writer', identifier, 'just wrote', txt)
        time.sleep(.5 + random.random())
    synchro.end_write()


def process_reader(identifier, synchro):
    synchro.start_read()
    position = 0
    result = ''
    while True:
        time.sleep(.1 + random.random())
        with open('LectRed_shared', 'r') as file_id:
            file_id.seek(position, 0)
            txt = file_id.read(1)
            if len(txt) == 0:
                break
            print('Reader', identifier, 'just read', txt)
            result += txt
            position += 1
    print(str(identifier) + ':', result)
    synchro.end_read()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: %s <Nb reader> <Nb writer> \n" % sys.argv[0])
        sys.exit(1)

    nb_reader = int(sys.argv[1])
    nb_writer = int(sys.argv[2])

    synchro = RW()

    # To initialize the common data
    with open('LectRed_shared', 'w') as file_id:
        file_id.write('')

    processes = []
    for id_writer in range(nb_writer):
        writer = Process(target=process_writer, args=(id_writer, synchro))
        writer.start()
        processes.append(writer)

    for id_reader in range(nb_reader):
        reader = Process(target=process_reader, args=(id_reader, synchro))
        reader.start()
        processes.append(reader)

    for process in processes:
        process.join()
