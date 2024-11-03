from __future__ import annotations

import numpy as np
from typing import List, Union

from .functions import (
    mod_polynomial,
    inverse_polynomial,
    fft_multiply_polynomials,
    karatsuba_multiply,
    format_polynomial,
)


class GaloisFieldExtensionElement:
    """
    Класс, представляющий собой элемент в расширении поля GF(p^n).

    Для корректного и удобного выполнения операций с экземплярами данного класса,
    у него переопределены многие специальные методы (сложение, вычитание, умножение, деление).
    """
    def __init__(self, p: int, coeffs: Union[List[int], np.ndarray], modulus_poly: np.poly1d):
        """
        Инициализация элемента поля GF(p^n).

        :param p: Характеристика поля.
        :param coeffs: Коэффициенты многочлена элемента.
        :param modulus_poly: Многочлен, который задаёт поле.
        """
        self.p = p
        self.modulus_poly = modulus_poly
        self.poly = mod_polynomial(np.poly1d(coeffs), modulus_poly, p)


    def calculate_value(self, x_element: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        """
        Вычисляет значение многочлена в заданной точке.

        :param x_element: Точка, в которой вычисляется многочлен.
        :return: Результат вычисления (как новый элемент поля).
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

    def __mul__(self, other: 'GaloisFieldExtensionElement') -> 'GaloisFieldExtensionElement':
        if self.p != other.p or not np.array_equal(self.modulus_poly.coeffs, other.modulus_poly.coeffs):
            raise ValueError("Элементы принадлежат разным полям.")

        product_coeffs = karatsuba_multiply(self.poly.coeffs.tolist(), other.poly.coeffs.tolist(), self.p)
        result_poly = mod_polynomial(np.poly1d(product_coeffs), self.modulus_poly, self.p)

        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __truediv__(self, other: GaloisFieldExtensionElement) -> GaloisFieldExtensionElement:
        inverse_poly = inverse_polynomial(other.poly, self.p, self.modulus_poly)
        result_poly = self.poly * inverse_poly

        return GaloisFieldExtensionElement(self.p, result_poly.coeffs, self.modulus_poly)

    def __repr__(self) -> str:
        return format_polynomial(self.poly)