import os
from sympy import symbols, Poly
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_irreducible(args):
    p, coeffs = args
    x = symbols('x')
    poly = Poly(coeffs, x, modulus=p)
    factors = poly.factor_list()
    # Проверяем, что факторизация содержит только один множитель, равный самому многочлену
    if len(factors[1]) == 1 and factors[1][0][0].degree() == poly.degree():
        return coeffs
    else:
        return None


def find_irreducible_polynomials_batch(p, n, batch_size, offset=0):
    total_combinations = (p - 1) * (p ** n)
    irreducible_polynomials = []

    end = min(offset + batch_size, total_combinations)
    args = []

    for index in range(offset, end):
        # Ведущий коэффициент от 1 до p-1
        leading_coeff = (index // (p ** n)) + 1
        rest_index = index % (p ** n)
        coeffs = []
        temp = rest_index
        for _ in range(n):
            coeffs.append(temp % p)
            temp = temp // p
        coeffs = coeffs[::-1]
        coeffs_full = [leading_coeff] + coeffs
        args.append((p, coeffs_full))

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_args = {executor.submit(is_irreducible, arg): arg for arg in args}
        for future in as_completed(future_to_args):
            res = future.result()
            if res is not None:
                irreducible_polynomials.append(res)

    return irreducible_polynomials