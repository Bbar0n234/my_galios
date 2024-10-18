from __future__ import annotations

import numpy as np
from typing import List

from .functions import mod_polynomial, inverse_polynomial


class GaloisFieldExtensionElement:
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


    def evaluate_at(self, x_element: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
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

        return GaloisFieldExtensionElement(self.p, result.coeffs, self.modulus_poly)


    def inverse(self) -> GaloisFieldExtensionElement:
        """
        Вычисляет мультипликативный обратный элемент в поле GF(p^n).

        :return: Обратный элемент поля.
        """
        inv_poly = inverse_polynomial(self.poly, self.p, self.modulus_poly)
        return GaloisFieldExtensionElement(self.p, inv_poly.coeffs, self.modulus_poly)

    def __add__(self, other: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        result_poly = self.poly + other.poly
        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __sub__(self, other: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        result_poly = self.poly - other.poly
        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __mul__(self, other: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        result_poly = self.poly * other.poly
        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __truediv__(self, other: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        inverse_poly = inverse_polynomial(other.poly, self.p, self.modulus_poly)
        result_poly = self.poly * inverse_poly
        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __repr__(self) -> str:
        coeffs = [int(c) for c in self.poly.coeffs]
        return f"GaloisFieldExtensionElement({coeffs})"