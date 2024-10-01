from __future__ import annotations

import numpy as np

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from funcs import GfpnEl

from sympy import isprime, Poly
from sympy.abc import x

from typing import List


class GFpn:
    """
    Класс, представляющий собой поле Галуа с характеристикой q = p ^ n.
    """

    def __init__(self, p: int, coeffs: List[int]) -> None:
        if not isprime(p):
            raise ValueError(f"Число {p} не является простым!")

        if not self.is_irreducable(coeffs, p):
            raise ValueError(f"Многочлен {coeffs} не является неприводимым над полем GF({p})")
                
        self.p = p
        self.__mod_poly = np.poly1d([coef % p for coef in coeffs]) # modulo_polynom


    @property
    def mod_poly(self):
        """
        Возвращает многочлен по модулю.
        """
        return self.__mod_poly
    

    @property
    def mod_poly_coeffs(self):
        """
        Возвращает коэффициенты многочлена по модулю.
        """
        return self.__mod_poly.coeffs
    

    def __str__(self):
        return f"GF({self.p}^{self.mod_poly_coeffs - 1})"
    
    
    @staticmethod
    def is_irreducable(coeffs: List[int], p: int) -> bool:
        """
        Проверяет, что многочлен неприводим над полем.
        """
        poly = Poly(coeffs[::-1], x, modulus=p)
        return poly.is_irreducible
    

    def create_el(self, coeffs: List[int]):
        """
        Создаёт элемент (многочлен) с коэффициентами, лежащими в поле GF(p^n)
        """
        return GfpnEl(self.p, coeffs, self.mod_poly)
    

    

    

