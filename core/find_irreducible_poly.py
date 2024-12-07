def poly_trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly

def poly_is_zero(poly):
    return all(c == 0 for c in poly)

def poly_degree(poly):
    return len(poly) - 1

def poly_add(a, b, p):
    length = max(len(a), len(b))
    res = [0]*length
    for i in range(length):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0
        res[i] = (ai + bi) % p
    return poly_trim(res)

def poly_sub(a, b, p):
    length = max(len(a), len(b))
    res = [0]*length
    for i in range(length):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0
        res[i] = (ai - bi) % p
    return poly_trim(res)

def poly_mul(a, b, p):
    res = [0]*(len(a)+len(b)-1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i+j] = (res[i+j] + a[i]*b[j]) % p
    return poly_trim(res)

def poly_scalar_mul(a, c, p):
    return poly_trim([(x*c) % p for x in a])

def poly_div_mod(a, b, p):
    # Деление многочленов с остатком: a = b*q + r
    # Возвращает (q, r) так, что deg(r)<deg(b)
    a = poly_trim(a[:])
    b = poly_trim(b[:])
    if poly_is_zero(b):
        raise ZeroDivisionError("Division by zero polynomial.")
    if poly_degree(a) < poly_degree(b):
        return [0], a  # q=0, r=a
    # Делим
    q = [0]*(poly_degree(a)-poly_degree(b)+1)
    # Обратный элемент для старшего коэф. b[-1]
    inv_lead = pow(b[-1], p-2, p)
    for i in range(poly_degree(a)-poly_degree(b), -1, -1):
        coeff = (a[poly_degree(b)+i]*inv_lead) % p
        q[i] = coeff
        # Вычитаем b*(x^i)*coeff из a
        for j in range(poly_degree(b)+1):
            a[i+j] = (a[i+j] - b[j]*coeff) % p
    return poly_trim(q), poly_trim(a)

def poly_gcd(a, b, p):
    a = poly_trim(a[:])
    b = poly_trim(b[:])
    while not poly_is_zero(b):
        _, r = poly_div_mod(a, b, p)
        a, b = b, r
    # Нормируем gcd: делаем старший коэффициент равным 1, если gcd не ноль
    if not poly_is_zero(a):
        inv_lead = pow(a[-1], p-2, p)
        a = poly_scalar_mul(a, inv_lead, p)
    return a

def poly_mod_exp(base, exp, mod_poly, p):
    # Возведение многочлена base в степень exp по модулю mod_poly
    result = [1]  # многочлен "1"
    cur = poly_div_mod(base, mod_poly, p)[1]
    e = exp
    while e > 0:
        if e & 1:
            mul_res = poly_mul(result, cur, p)
            _, result = poly_div_mod(mul_res, mod_poly, p)
        sqr_res = poly_mul(cur, cur, p)
        _, cur = poly_div_mod(sqr_res, mod_poly, p)
        e >>= 1
    return result

def poly_pow_mod(base, exp, mod_poly, p):
    # Обёртка для удобства, можно использовать poly_mod_exp напрямую
    return poly_mod_exp(base, exp, mod_poly, p)

def is_irreducible_benor(args):
    p, poly_coeffs = args
    poly = poly_trim(poly_coeffs[:])

    if poly_is_zero(poly):
        return None

    n = poly_degree(poly)

    if n == 0 or (poly[0] == 0 and n > 1):
        return None
    if n == 1:
        return poly[::-1]

    # x многочлен будет [0,1]
    x_poly = [0, 1]
    m = n // 2

    # Тест Бен-Ора
    for i in range(1, m + 1):
        exp_val = p**i
        x_p_i = poly_pow_mod(x_poly, exp_val, poly, p)
        tmp = poly_sub(x_p_i, x_poly, p)
        g = poly_gcd(poly, tmp, p)
        if poly_is_zero(tmp) or poly_degree(g) > 0:
            return None

    return poly[::-1]

def find_irreducible_polynomials(p, n):
    total_combinations = (p - 1) * (p ** n)

    for index in range(total_combinations):
        # Ведущий коэффициент от 1 до p-1
        leading_coeff = (index // (p ** n)) + 1
        rest_index = index % (p ** n)
        coeffs = []
        temp = rest_index
        for _ in range(n):
            coeffs.append(temp % p)
            temp = temp // p
        coeffs = coeffs[::-1]  # Переворачиваем, чтобы старшие степени были впереди
        coeffs_full = [leading_coeff] + coeffs

        result = is_irreducible_benor((p, coeffs_full[::-1]))

        if result is not None:
            yield result