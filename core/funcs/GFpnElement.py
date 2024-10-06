from __future__ import annotations

import numpy as np

from typing import List


def mod_coeffs(coeffs: np.ndarray, p: int) -> np.ndarray:
    """
    Применяет модуль p к каждому коэффициенту.

    :param coeffs: Массив коэффициентов многочлена.
    :param p: Характеристика поля.
    :return: Массив коэффициентов по модулю p.
    """
    return np.array([el % p for el in coeffs], dtype=int)


def mod_polynomial(poly1: np.poly1d, poly2: np.poly1d, p: int) -> np.poly1d:
    """
    Вычисляет poly1 mod poly2 над GF(p).

    :param poly1: Делимое многочлен.
    :param poly2: Делитель многочлен.
    :param p: Характеристика поля.
    :return: Остаток от деления poly1 на poly2 по модулю p.
    """
    _, remainder = np.polydiv(poly1, poly2)
    coeffs = mod_coeffs(remainder.coeffs, p)
    return np.poly1d(coeffs)


def mod_pow_polynomial(poly: np.poly1d, exponent: int, p: int, modulus_poly: np.poly1d) -> np.poly1d:
    """
    Эффективно вычисляет (poly ** exponent) mod modulus_poly над GF(p).

    :param poly: Базовый многочлен.
    :param exponent: Показатель степени.
    :param p: Характеристика поля.
    :param modulus_poly: Модульный многочлен.
    :return: Результат возведения в степень по модулю modulus_poly.
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


class GFpnElement:
    """
    Класс, представляющий элемент в поле GF(p^n).
    """
    def __init__(self, p: int, coeffs: List[int], modulus_poly: np.poly1d):
        """
        Инициализация элемента поля GF(p^n).

        :param p: Характеристика поля.
        :param coeffs: Коэффициенты многочлена элемента.
        :param modulus_poly: Модульный многочлен поля.
        """
        self.p = p
        self.modulus_poly = modulus_poly

        _, remainder = np.polydiv(np.poly1d(coeffs), modulus_poly)
        self.poly = np.poly1d([coef % p for coef in remainder.coeffs])


    def evaluate_at(self, x_element: GFpnElement) -> GFpnElement:
        """
        Вычисляет значение многочлена в заданном элементе поля.

        :param x_element: Значение, в котором вычисляется многочлен.
        :return: Результат вычисления как элемент поля.
        """
        result = np.poly1d([0])
        x_power = np.poly1d([1])

        for coef in self.poly.coeffs[::-1]:
            term = np.poly1d([coef]) * x_power
            result = mod_polynomial(result + term, self.modulus_poly, self.p)
            x_power = mod_polynomial(x_power * x_element.poly, self.modulus_poly, self.p)

        return GFpnElement(self.p, result.coeffs, self.modulus_poly)


    def inverse(self) -> GFpnElement:
        """
        Вычисляет мультипликативный обратный элемент в поле GF(p^n).

        :return: Обратный элемент поля.
        """
        inv_poly = inverse_polynomial(self.poly, self.p, self.modulus_poly)
        return GFpnElement(self.p, inv_poly.coeffs, self.modulus_poly)

    def __add__(self, other: GFpnElement) -> GFpnElement:
        result_poly = self.poly + other.poly
        return GFpnElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __sub__(self, other: GFpnElement) -> GFpnElement:
        result_poly = self.poly - other.poly
        return GFpnElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __mul__(self, other: GFpnElement) -> GFpnElement:
        result_poly = self.poly * other.poly
        return GFpnElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __truediv__(self, other: GFpnElement) -> GFpnElement:
        inverse_poly = inverse_polynomial(other.poly, self.p, self.modulus_poly)
        result_poly = self.poly * inverse_poly
        return GFpnElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __repr__(self) -> str:
        coeffs = [int(c) for c in self.poly.coeffs]
        return f"GFpnElement({coeffs})"