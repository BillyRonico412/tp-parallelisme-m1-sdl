def syracuse(n):
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def nb_syracuse(n):
    res = 0
    while n != 1:
        res += 1
        n = syracuse(n)
    return res

# La version 2 est beaucoup plus rapide car moins de traitement sur les intervales