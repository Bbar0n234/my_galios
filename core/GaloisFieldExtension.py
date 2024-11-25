from __future__ import annotations

import numpy as np

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from elements import GaloisFieldExtensionElement

from sympy import isprime, Poly
from sympy.abc import x

from typing import List


class GaloisFieldExtension:
    """
    Класс, представляющий поле Галуа GF(p^n).
    """
    def __init__(self, p: int, modulus_coeffs: List[int]) -> None:
        """
        Инициализация поля Галуа GF(p^n).

        :param p: Простое число, характеристика поля.
        :param modulus_coeffs: Коэффициенты неприводимого многочлена, задающего расширение поля.
        """
        if not isprime(p):
            raise ValueError(f"Число {p} не является простым!")

        if not self._is_irreducible(modulus_coeffs, p):
            raise ValueError(f"Многочлен {modulus_coeffs} не является неприводимым над полем GF({p})")
                
        self.p = p
        self.modulus_polynomial = np.poly1d([coef % p for coef in modulus_coeffs])

    @staticmethod
    def _is_irreducible(coeffs: List[int], p: int) -> bool:
        """
        Проверяет, что многочлен неприводим над полем GF(p).

        :param coeffs: Коэффициенты многочлена.
        :param p: Характеристика поля.
        :return: True - если многочлен неприводим, иначе False.
        """
        poly = Poly(coeffs[::-1], x, modulus=p)

        return poly.is_irreducible

    def create_element(self, coeffs: List[int]) -> GaloisFieldExtensionElement:
        """
        Создает элемент поля GF(p^n).

        :param coeffs: Коэффициенты многочлена.
        :return: новый элемент (многочлен).
        """
        return GaloisFieldExtensionElement(self.p, coeffs, self.modulus_polynomial)

    def __str__(self) -> str:
        return f"GF({self.p}^{len(self.modulus_polynomial.coeffs) - 1})"
