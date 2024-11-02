import os
from sympy import symbols, Poly
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_args = {executor.submit(is_irreducible, arg): arg for arg in args}
        for future in as_completed(future_to_args):
            res = future.result()
            if res is not None:
                irreducible_polynomials.append(res)

    return irreducible_polynomials