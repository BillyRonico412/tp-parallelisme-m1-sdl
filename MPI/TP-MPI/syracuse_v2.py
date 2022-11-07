from mpi4py import MPI
import time
from syracuse import nb_syracuse

if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nb = 1000000

    start_time = time.time()

    max_syracuse_on_process = max([nb_syracuse(i) for i in range(rank + 1, nb + 1, size)])
    max_total_syracuse = comm.reduce(max_syracuse_on_process, op=MPI.MAX, root=0)

    if rank == 0:
        end_time = time.time()
        print("time : ", end_time - start_time)
        print("max_syracuse entre 1 à", nb, ":", max_total_syracuse)




