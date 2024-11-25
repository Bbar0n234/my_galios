import numpy as np
from typing import List


def karatsuba_multiply(coeffs1: List[int], coeffs2: List[int], p: int) -> List[int]:
    """
    Умножает два многочлена с использованием алгоритма Карацубы с приведением по модулю p.
    Коэффициенты передаются от старшей степени к младшей.
    
    :param coeffs1: Коэффициенты первого многочлена (от старшей степени к младшей).
    :param coeffs2: Коэффициенты второго многочлена (от старшей степени к младшей).
    :param p: Модуль для конечного поля.
    :return: Коэффициенты результирующего многочлена (от старшей степени к младшей).
    """
    # Переворачиваем коэффициенты для удобства (младшая к старшей)
    coeffs1_rev = coeffs1[::-1]
    coeffs2_rev = coeffs2[::-1]
    
    def karatsuba_recursive(a: List[int], b: List[int], p: int) -> List[int]:
        n = max(len(a), len(b))
        
        # Добавляем нули, чтобы длины были равны и равны степени двойки
        while len(a) < n:
            a.append(0)
        while len(b) < n:
            b.append(0)
        
        # Выход из рекурсии, когда многочлены уже достаточно малой степени
        if n <= 1:
            return multiply_naive(a, b, p)
        
        m = n // 2
        
        # Разделяем многочлены на младшие и старшие части
        low1 = a[:m]
        high1 = a[m:]
        low2 = b[:m]
        high2 = b[m:]
        
        # Рекурсивное умножение
        z0 = karatsuba_recursive(low1, low2, p)
        z2 = karatsuba_recursive(high1, high2, p)
        
        # Сложение младших и старших частей
        sum1 = [(x + y) % p for x, y in zip_extended(low1, high1)]
        sum2 = [(x + y) % p for x, y in zip_extended(low2, high2)]
        
        # Рекурсивное умножение сумм
        z1 = karatsuba_recursive(sum1, sum2, p)
        
        # Вычитание z0 и z2 из z1
        z1 = [(c - a - b) % p for c, a, b in zip_extended(z1, z0, z2)]
        
        # Сборка итогового многочлена
        result = [0] * (2 * n)
        
        for i in range(len(z0)):
            result[i] = (result[i] + z0[i]) % p
        for i in range(len(z1)):
            result[i + m] = (result[i + m] + z1[i]) % p
        for i in range(len(z2)):
            result[i + 2 * m] = (result[i + 2 * m] + z2[i]) % p
        
        # Удаление ведущих нулей
        while len(result) > 1 and result[-1] == 0:
            result.pop()
        
        return result
    
    # Запуск рекурсивного умножения
    result_rev = karatsuba_recursive(coeffs1_rev.copy(), coeffs2_rev.copy(), p)
    
    # Переворачиваем обратно к старшей степени
    result = result_rev[::-1]
    
    return result


def multiply_naive(coeffs1: List[int], coeffs2: List[int], p: int) -> List[int]:
    """
    Наивное умножение двух многочленов с приведением по модулю p.

    :param coeffs1: Коэффициенты первого многочлена (от старшей степени к младшей).
    :param coeffs2: Коэффициенты второго многочлена (от старшей степени к младшей).
    :param p: Модуль для конечного поля.
    :return: Коэффициенты результирующего многочлена (от старшей степени к младшей).
    """
    # Переворачиваем коэффициенты для удобства (младшая к старшей)
    coeffs1_rev = coeffs1[::-1]
    coeffs2_rev = coeffs2[::-1]

    # Вычисляем степень результирующего многочлена
    result_degree = len(coeffs1_rev) + len(coeffs2_rev) - 1
    result_rev = [0] * result_degree

    # Наивное умножение
    for i in range(len(coeffs1_rev)):
        for j in range(len(coeffs2_rev)):
            result_rev[i + j] = (result_rev[i + j] + coeffs1_rev[i] * coeffs2_rev[j]) % p

    # Удаляем ведущие нули (в низшей степени после переворота)
    while len(result_rev) > 1 and result_rev[-1] == 0:
        result_rev.pop()

    # Переворачиваем обратно к старшей степени
    result = result_rev[::-1]

    return result


def zip_extended(*args):
    """
    Функция для сложения списков разной длины.

    :param args: Много списков для сложения.
    :return: Список кортежей.
    """
    max_len = max(len(arg) for arg in args)
    extended_args = [arg + [0] * (max_len - len(arg)) for arg in args]
    return zip(*extended_args)

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
    Приводит коэффициенты многочлена по модулю p.

    :param coeffs: Массив коэффициентов многочлена.
    :param p: Характеристика конечного поля (модуль).
    :return: Массив коэффициентов, приведённых по модулю p.
    """
    return np.array([el % p for el in coeffs], dtype=int)


def inverse_in_field(element: int, p: int) -> int:
    """
    Вычисляет мультипликативный обратный элемент в поле GF(p).

    :param element: Элемент конечного поля GF(p).
    :param p: Характеристика конечного поля.
    :return: Обратный элемент в поле GF(p).
    """
    return pow(element, p - 2, p)


def poly_mul(poly1: np.poly1d, poly2: np.poly1d, p: int) -> np.poly1d:
    """
    Умножает два многочлена и приводит коэффициенты произведения по модулю p.

    :param poly1: Первый многочлен.
    :param poly2: Второй многочлен.
    :param p: Характеристика конечного поля.
    :return: Произведение двух многочленов по модулю p.
    """
    product_coeffs = np.convolve(poly1.coeffs, poly2.coeffs)
    product_coeffs = mod_coeffs(product_coeffs, p)

    return np.poly1d(product_coeffs)


def mod_polynomial(poly1: np.poly1d, poly2: np.poly1d, p: int) -> np.poly1d:
    """
    Делит многочлен poly1 на poly2 и возвращает остаток от деления по модулю p.

    :param poly1: Делимый многочлен.
    :param poly2: Делитель многочлен.
    :param p: Характеристика конечного поля.
    :return: Остаток от деления poly1 на poly2 по модулю p.
    """
    poly1_coeffs = mod_coeffs(poly1.coeffs, p).tolist()
    poly2_coeffs = mod_coeffs(poly2.coeffs, p).tolist()

    remainder = poly1_coeffs[:]

    while len(remainder) >= len(poly2_coeffs):
        coeff = (remainder[0] * inverse_in_field(poly2_coeffs[0], p)) % p
        for i in range(len(poly2_coeffs)):
            remainder[i] = (remainder[i] - coeff * poly2_coeffs[i]) % p
        remainder = remainder[1:] if remainder[0] == 0 else remainder

    if not remainder:
        remainder = [0]

    return np.poly1d(remainder)


def mod_pow_polynomial(poly: np.poly1d, e: int, p: int, mod_poly: np.poly1d) -> np.poly1d:
    """
    Возводит многочлен в степень e по модулю многочлена mod_poly в поле GF(p).

    :param poly: Многочлен для возведения в степень.
    :param e: Степень.
    :param p: Характеристика конечного поля.
    :param mod_poly: Модульный многочлен, по которому происходит деление.
    :return: Многочлен, возведённый в степень e по модулю mod_poly.
    """
    
    result = np.poly1d([1])
    base = poly

    e %= p ** (len(mod_poly.coeffs) - 1) - 1
    if e == 0:
        return result

    while e > 0:
        if e % 2 == 1:
            result = poly_mul(result, base, p)
            result = mod_polynomial(result, mod_poly, p)
        base = poly_mul(base, base, p)
        base = mod_polynomial(base, mod_poly, p)
        e //= 2

    return result


def inverse_polynomial(poly: np.poly1d, p: int, modulus_poly: np.poly1d) -> np.poly1d:
    """
    Вычисляет обратный многочлен по модулю другого многочлена в поле GF(p^n).

    :param poly: Многочлен, для которого нужно найти обратный.
    :param p: Характеристика конечного поля.
    :param modulus_poly: Модульный многочлен, по которому выполняется операция.
    :return: Обратный многочлен по модулю modulus_poly в поле GF(p^n).
    """
    if len(poly.coeffs) == 1:
        inverse_el = inverse_in_field(int(poly.coeffs[0]), p)
        return np.poly1d([inverse_el])

    return mod_pow_polynomial(poly, p ** (len(modulus_poly.coeffs) - 1) - 2, p, modulus_poly)



