def poly_trim(poly):
    """Удаляет старшие нулевые коэффициенты из многочлена."""
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_is_zero(poly):
    """Проверяет, является ли многочлен нулевым."""
    return all(c == 0 for c in poly)


def poly_degree(poly):
    """Возвращает степень многочлена."""
    return len(poly) - 1


def poly_add(a, b, p):
    """Складывает два многочлена по модулю p."""
    length = max(len(a), len(b))
    res = [0] * length
    for i in range(length):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0
        res[i] = (ai + bi) % p
    return poly_trim(res)


def poly_sub(a, b, p):
    """Вычитает многочлен b из a по модулю p."""
    length = max(len(a), len(b))
    res = [0] * length
    for i in range(length):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0
        res[i] = (ai - bi) % p
    return poly_trim(res)


def poly_mul(a, b, p):
    """Умножает два многочлена по модулю p."""
    res = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i + j] = (res[i + j] + a[i] * b[j]) % p
    return poly_trim(res)


def poly_scalar_mul(a, c, p):
    """Умножает многочлен на скаляр c по модулю p."""
    return poly_trim([(x * c) % p for x in a])


def poly_div_mod(a, b, p):
    """
    Делит многочлен a на b с остатком по модулю p.
    Возвращает кортеж (частное, остаток), где степень остатка < степени b.
    """
    a = poly_trim(a[:])
    b = poly_trim(b[:])
    if poly_is_zero(b):
        raise ZeroDivisionError("Division by zero polynomial.")
    if poly_degree(a) < poly_degree(b):
        return [0], a  # q=0, r=a
    q = [0] * (poly_degree(a) - poly_degree(b) + 1)
    inv_lead = pow(b[-1], p - 2, p)  # Обратный элемент для старшего коэффициента
    for i in range(poly_degree(a) - poly_degree(b), -1, -1):
        coeff = (a[poly_degree(b) + i] * inv_lead) % p
        q[i] = coeff
        for j in range(poly_degree(b) + 1):
            a[i + j] = (a[i + j] - b[j] * coeff) % p
    return poly_trim(q), poly_trim(a)


def poly_gcd(a, b, p):
    """Находит наибольший общий делитель (НОД) двух многочленов по модулю p."""
    a = poly_trim(a[:])
    b = poly_trim(b[:])
    while not poly_is_zero(b):
        _, r = poly_div_mod(a, b, p)
        a, b = b, r
    if not poly_is_zero(a):
        inv_lead = pow(a[-1], p - 2, p)
        a = poly_scalar_mul(a, inv_lead, p)
    return a


def poly_mod_exp(base, exp, mod_poly, p):
    """
    Возводит многочлен base в степень exp по модулю mod_poly и p.
    Использует метод быстрого возведения в степень.
    """
    result = [1]  # Многочлен "1"
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
    """Обёртка для возведения в степень по модулю (poly_mod_exp)."""
    return poly_mod_exp(base, exp, mod_poly, p)


def is_irreducible_benor(args):
    """
    Реализует тест Бен-Ора на неприводимость многочлена над конечным полем.
    Проверяет, является ли многочлен неприводимым.

    Параметры:
    - p: модуль конечного поля (размер поля).
    - poly_coeffs: коэффициенты проверяемого многочлена.

    Возвращает:
    - Перевёрнутый список коэффициентов, если многочлен неприводим.
    - None, если многочлен приводим.
    """
    p, poly_coeffs = args
    poly = poly_trim(poly_coeffs[:])

    if poly_is_zero(poly):
        return None

    n = poly_degree(poly)

    if n == 0 or (poly[0] == 0 and n > 1):
        return None
    if n == 1:
        return poly[::-1]

    x_poly = [0, 1]  # Многочлен x
    m = n // 2

    for i in range(1, m + 1):
        exp_val = p ** i
        x_p_i = poly_pow_mod(x_poly, exp_val, poly, p)
        tmp = poly_sub(x_p_i, x_poly, p)
        g = poly_gcd(poly, tmp, p)
        if poly_is_zero(tmp) or poly_degree(g) > 0:
            return None

    return poly[::-1]