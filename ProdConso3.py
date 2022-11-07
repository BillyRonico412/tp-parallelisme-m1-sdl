import time
import random
from multiprocessing import Process, Lock, Condition, Value, Array

import sys

if len(sys.argv) != 6:
    print("Usage: %s <Nb Prod <= 20> <Nb Conso <= 20> <Nb Cases <= 20> <Nb Times Prod <= 10> <Nb Times Cons <= 10>" %
          sys.argv[0])
    sys.exit(1)

nb_prod = int(sys.argv[1])
nb_cons = int(sys.argv[2])
nb_cases = int(sys.argv[3])

nb_times_prod = int(sys.argv[4])
nb_times_cons = int(sys.argv[5])

### Monitor start

# On ajoute un verrous
lock = Lock()

# On rajoute les deux conditions correspondant au producteur et consommateur
c_prod = Condition(lock)
c_cons = (Condition(lock), Condition(lock))

# On doit compter les producteurs et consommateur en attente
nb_prod_attente = Value('i', 0)
nb_cons_attente = Array('i', [0, 0])

# On a besoin du nombre de case vide
nb_cases_vides = Value('i', nb_cases)

storage_val = Array('i', [-1] * nb_cases)
storage_type = Array('i', [-1] * nb_cases)
ptr_prod = Value('i', 0)
ptr_cons = Value('i', 0)
producers, consumers = [], []


def produce(msg_val, msg_type, msg_source):
    with lock:
        nb_prod_attente.value += 1
        # Condition de blocage
        while nb_cases_vides.value == 0:
            c_prod.wait()

        est_vide = all(map(lambda x: x == -1, storage_val))

        nb_prod_attente.value -= 1
        position = ptr_prod.value
        storage_val[position] = msg_val
        storage_type[position] = msg_type
        ptr_prod.value = (position + 1) % nb_cases
        print('%3d produced %3d (type:%d) in place %3d and the buffer is\t\t %s %s' %
              (msg_source, msg_val, msg_type, position, storage_val[:], storage_type[:]))

        nb_cases_vides.value -= 1

        if est_vide:
            c_cons[msg_type].notify()

def consume(id_cons, msg_type):
    with lock:
        nb_cons_attente[msg_type] += 1

        # Condition de blocage
        while nb_cases_vides.value == nb_cases or storage_type[ptr_cons.value] != msg_type:
            c_cons[msg_type].wait()

        nb_cons_attente[msg_type] -= 1

        position = ptr_cons.value
        result = storage_val[position]
        result_type = storage_type[position]
        storage_val[position] = -1
        storage_type[position] = -1
        ptr_cons.value = (position + 1) % nb_cases
        print('\t%3d consumed %3d (type:%d) in place %3d and the buffer is\t %s %s' %
              (id_cons, result, result_type, position, storage_val[:], storage_type[:]))

        nb_cases_vides.value += 1

        prochain_type = storage_type[ptr_cons.value]

        if prochain_type != -1 and nb_cons_attente[prochain_type] != 0:
            c_cons[prochain_type].notify()
        else:
            c_prod.notify()

        return result


#### Monitor end

def producer(msg_val, msg_type, msg_source):
    for _ in range(nb_times_prod):
        time.sleep(.1 + random.random())
        produce(msg_val, msg_type, msg_source)
        msg_val += 1


def consumer(id_cons, msg_type):
    for _ in range(nb_times_cons):
        time.sleep(.5 + random.random())
        consume(id_cons, msg_type)


if __name__ == '__main__':
    for id_prod in range(nb_prod):
        msg_val_start, msg_type, msg_source = id_prod * nb_times_prod, id_prod % 2, id_prod
        prod = Process(target=producer, args=(msg_val_start, msg_type, msg_source))
        prod.start()
        producers.append(prod)

    for id_cons in range(nb_cons):
        msg_type = id_cons % 2
        cons = Process(target=consumer, args=(id_cons, msg_type))
        cons.start()
        consumers.append(cons)

    for prod in producers:
        prod.join()

    for cons in consumers:
        cons.join()
