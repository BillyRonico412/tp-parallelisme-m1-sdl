#! /usr/bin/python3

import time
import random
from mpi4py import MPI

if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nb = 10000001
    inside = 0
    random.seed(0)

    start_time = time.time()

    part = nb // size
    reste = nb % size

    if rank < reste:
        part += 1

    for _ in range(part):
        x = random.random()
        y = random.random()
        if x*x + y*y <= 1:
            inside +=1

    somme_inside = comm.reduce(inside, op=MPI.SUM, root=0)

    end_time = time.time()

    if rank == 0:
        print("Pi =", 4 * somme_inside / nb, "in ", end_time - start_time, 'seconds')


