import time
import random
from multiprocessing import Process, Lock, Condition, Value, Array

import sys

if len(sys.argv) != 6:
    print("Usage: %s <Nb Prod <= 20> <Nb Conso <= 20> <Nb Cases <= 20> <Nb Times Prod <= 10> <Nb Times Cons <= 10>" % sys.argv[0])
    sys.exit(1)

nb_prod = int(sys.argv[1])
nb_cons = int(sys.argv[2])
nb_cases = int(sys.argv[3])

nb_times_prod = int(sys.argv[4])
nb_times_cons = int(sys.argv[5])

### Monitor start
storage_val = Array('i', [-1] * nb_cases)
storage_type = Array('i', [-1] * nb_cases)
ptr_prod = Value('i', 0)
ptr_cons = Value('i', 0)
producers, consumers = [], []


def produce(msg_val, msg_type, msg_source):
    position = ptr_prod.value
    storage_val[position] = msg_val
    storage_type[position] = msg_type
    ptr_prod.value = (position + 1) % nb_cases
    print('%3d produced %3d (type:%d) in place %3d and the buffer is\t\t %s' %
          (msg_source, msg_val, msg_type, position, storage_val[:]))


def consume(id_cons):
    position = ptr_cons.value
    result = storage_val[position]
    result_type = storage_type[position]
    storage_val[position] = -1
    storage_type[position] = -1
    ptr_cons.value = (position + 1) % nb_cases
    print('\t%3d consumed %3d (type:%d) in place %3d and the buffer is\t %s' %
          (id_cons, result, result_type, position, storage_val[:]))
    return result


#### Monitor end

def producer(msg_val, msg_type, msg_source):
    for _ in range(nb_times_prod):
        time.sleep(.1 + random.random())
        produce(msg_val, msg_type, msg_source)
        msg_val += 1


def consumer(id_cons):
    for _ in range(nb_times_cons):
        time.sleep(.5 + random.random())
        consume(id_cons)


if __name__ == '__main__':
    for id_prod in range(nb_prod):
        msg_val_start, msg_type, msg_source = id_prod * nb_times_prod, id_prod % 2, id_prod
        prod = Process(target=producer, args=(msg_val_start, msg_type, msg_source))
        prod.start()
        producers.append(prod)

    for id_cons in range(nb_cons):
        cons = Process(target=consumer, args=(id_cons,))
        cons.start()
        consumers.append(cons)

    for prod in producers:
        prod.join()

    for cons in consumers:
        cons.join()
