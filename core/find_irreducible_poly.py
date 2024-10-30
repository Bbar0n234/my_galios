from sympy import symbols, Poly
from multiprocessing import Pool, cpu_count


def is_irreducible(args):
    p, coeffs = args
    x = symbols('x')
    coeffs_full = [1] + list(coeffs)
    poly = Poly(coeffs_full, x, modulus=p)
    factors = poly.factor_list()
    if len(factors[1]) == 1 and factors[1][0][0].degree() == poly.degree():
        return coeffs_full
    else:
        return None

def find_irreducible_polynomials_batch(p, n, batch_size, offset=0):
    total_combinations = p ** n
    irreducible_polynomials = []

    end = min(offset + batch_size, total_combinations)
    args = []

    for index in range(offset, end):
        coeffs = []
        idx = index
        for _ in range(n):
            coeffs.append(idx % p)
            idx = idx // p
        coeffs = coeffs[::-1]
        args.append((p, tuple(coeffs)))

    num_processes = cpu_count()
    pool = Pool(processes=num_processes)
    results = pool.imap_unordered(is_irreducible, args, chunksize=1000)
    pool.close()

    for res in results:
        if res is not None:
            irreducible_polynomials.append(res)

    pool.join()

    return irreducible_polynomials
