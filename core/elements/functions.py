import numpy as np
from typing import List

from typing import List


def karatsuba_multiply(coeffs1: List[int], coeffs2: List[int], p: int) -> List[int]:
    """
    Умножает два многочлена с использованием алгоритма Карацубы с приведением по модулю p.

    :param coeffs1: Коэффициенты первого многочлена (от младшей степени к старшей).
    :param coeffs2: Коэффициенты второго многочлена (от младшей степени к старшей).
    :param p: Модуль для конечного поля.
    :return: Коэффициенты результирующего многочлена (от младшей степени к старшей).
    """
    n = max(len(coeffs1), len(coeffs2))

    # Для выхода из рекурсии, когда многочлены уже достаточно малой степени
    if n <= 1:
        return multiply_naive(coeffs1, coeffs2, p)

    # Деление степени пополам
    m = n // 2

    # Разделяем многочлены на младшие и старшие части
    low1 = coeffs1[:m]
    high1 = coeffs1[m:]
    low2 = coeffs2[:m]
    high2 = coeffs2[m:]

    # Рекурсивное умножение
    z0 = karatsuba_multiply(low1, low2, p)
    z2 = karatsuba_multiply(high1, high2, p)

    # Сложение младших и старших частей
    sum1 = [(a + b) % p for a, b in zip_extended(low1, high1)]
    sum2 = [(a + b) % p for a, b in zip_extended(low2, high2)]

    # Рекурсивное умножение сумм
    z1 = karatsuba_multiply(sum1, sum2, p)

    # Вычитание z0 и z2 из z1
    z1 = [(c - a - b) % p for c, a, b in zip_extended(z1, z0, z2)]

    # Сборка итогового многочлена
    result = [0] * (len(z0) + 2 * m)

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


def multiply_naive(coeffs1: List[int], coeffs2: List[int], p: int) -> List[int]:
    """
    Наивное умножение двух многочленов с приведением по модулю p.

    :param coeffs1: Коэффициенты первого многочлена (от младшей степени к старшей).
    :param coeffs2: Коэффициенты второго многочлена (от младшей степени к старшей).
    :param p: Модуль для конечного поля.
    :return: Коэффициенты результирующего многочлена (от младшей степени к старшей).
    """
    result_degree = len(coeffs1) + len(coeffs2) - 1
    result = [0] * result_degree
    for i in range(len(coeffs1)):
        for j in range(len(coeffs2)):
            result[i + j] = (result[i + j] + coeffs1[i] * coeffs2[j]) % p
    # Удаляем ведущие нули
    while len(result) > 1 and result[-1] == 0:
        result.pop()
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



def fft_multiply_polynomials(coeffs1: List[int], coeffs2: List[int]) -> List[int]:
    """
    Умножает два многочлена с помощью FFT и возвращает коэффициенты результата.

    :param coeffs1: Коэффициенты первого многочлена (от старшей степени к младшей).
    :param coeffs2: Коэффициенты второго многочлена (от старшей степени к младшей).
    :return: Коэффициенты результирующего многочлена (от старшей степени к младшей).
    """
    # Переворачиваем коэффициенты для удобства (от младшей степени к старшей)
    A = np.array(coeffs1[::-1], dtype=np.float64)
    B = np.array(coeffs2[::-1], dtype=np.float64)

    n = 1
    while n < len(A) + len(B):
        n <<= 1  # Удваиваем до ближайшей степени двойки

    A = np.pad(A, (0, n - len(A)), 'constant')
    B = np.pad(B, (0, n - len(B)), 'constant')

    # Выполняем FFT
    FA = np.fft.fft(A)
    FB = np.fft.fft(B)

    # Поэлементное умножение в частотной области
    FC = FA * FB

    # Обратное FFT
    C = np.fft.ifft(FC)

    # Округление и приведение к целым числам
    C = np.round(C.real).astype(np.int64)

    # Обработка переноса
    carry = 0
    for i in range(len(C)):
        total = C[i] + carry
        C[i] = total % 10
        carry = total // 10

    # Преобразуем обратно к порядку от старшей степени к младшей
    C = C[:len(A) + len(B) - 1]
    result_coeffs = C[::-1].tolist()

    while len(result_coeffs) > 1 and result_coeffs[0] == 0:
        result_coeffs.pop(0)

    return result_coeffs


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



