import numpy as np


def format_polynomial(poly: np.poly1d) -> str:
    """
    Преобразует многочлен в читаемую строку.

    :param poly: Многочлен в формате numpy.poly1d.
    :return: Строка, представляющая многочлен.
    """
    coeffs = poly.coeffs
    degree = len(coeffs) - 1
    terms = []
    for i, coef in enumerate(coeffs):
        current_degree = degree - i
        coef = int(coef)
        if coef == 0:
            continue

        if abs(coef) == 1 and current_degree != 0:
            coef_str = "-" if coef == -1 else ""
        else:
            coef_str = str(coef)

        if current_degree > 1:
            term = f"{coef_str}x^{current_degree}"
        elif current_degree == 1:
            term = f"{coef_str}x"
        else:
            term = f"{coef_str}"
        terms.append(term)

    if not terms:
        return "0"
    
    polynomial = " + ".join(terms)
    polynomial = polynomial.replace("+ -", "- ")

    return polynomial


def mod_coeffs(coeffs: np.ndarray, p: int) -> np.ndarray:
    """
    Берёт каждый коэффициент многочлена по модулю p

    :param coeffs: Массив коэффициентов многочлена.
    :param p: Характеристика поля.
    :return: Массив коэффициентов по модулю p.
    """
    return np.array([el % p for el in coeffs], dtype=int)


def mod_polynomial(poly1: np.poly1d, poly2: np.poly1d, p: int) -> np.poly1d:
    """
    Делит два многочлена в поле GF(p) (без приведения по модулю многочлена).

    :param poly1: Делимый многочлен.
    :param poly2: Делитель многочлен.
    :param p: Характеристика поля.
    :return: Остаток от деления poly1 на poly2 по модулю p.
    """
    _, remainder = np.polydiv(poly1, poly2)
    coeffs = mod_coeffs(remainder.coeffs, p)
    return np.poly1d(coeffs)


def mod_pow_polynomial(poly: np.poly1d, exponent: int, p: int, modulus_poly: np.poly1d) -> np.poly1d:
    """
    Возводит многочлен в степень с помощью алгоритмы двоичного возведения.

    :param poly: Базовый многочлен.
    :param exponent: Показатель степени.
    :param p: Характеристика поля.
    :param modulus_poly: Модульный многочлен.
    :return: Результат возведения многочлена в степень по модулю другого многочлена.
    """
    result = np.poly1d([1])
    base = np.poly1d(poly.coeffs)

    exponent_mod = p ** (len(modulus_poly.coeffs) - 1) - 1
    exponent = exponent % exponent_mod
    if exponent == 0:
        return result

    while exponent > 0:
        if exponent % 2 == 1:
            result = mod_polynomial(result * base, modulus_poly, p)
        base = mod_polynomial(base * base, modulus_poly, p)
        exponent = exponent // 2

    return result


def inverse_in_field(element: int, p: int) -> int:
    """
    Вычисляет мультипликативный обратный элемента в GF(p).

    :param element: Элемент поля.
    :param p: Характеристика поля.
    :return: Обратный элемент.
    """
    return pow(element, p - 2, p)


def inverse_polynomial(poly: np.poly1d, p: int, modulus_poly: np.poly1d) -> np.poly1d:
    """
    Вычисляет мультипликативный обратный многочлена в GF(p^n).

    :param poly: Многочлен для обращения.
    :param p: Характеристика поля.
    :param modulus_poly: Модульный многочлен.
    :return: Обратный многочлен.
    """
    if len(poly.coeffs) == 1:
        inverse_el = inverse_in_field(int(poly.coeffs[0]), p)
        return np.poly1d([inverse_el])

    return mod_pow_polynomial(poly, p ** (len(modulus_poly.coeffs) - 1) - 2, p, modulus_poly)

