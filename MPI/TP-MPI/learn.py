from mpi4py import MPI
import time

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        pair = [0, 2, 4, 6]
    else:
        pair = None

    x = comm.scatter(sendobj=pair, root=0)

    print(x)
