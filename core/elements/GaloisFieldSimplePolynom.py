import numpy as np
from .functions import (
    format_polynomial,
    karatsuba_multiply,
)
from .GaloisFieldSimpleElement import GaloisFieldSimpleElement


class GaloisFieldSimplePolynom:
    """
    Класс для работы с многочленами в простом поле GF(p).

    В отличие от работы с многочленами в расширении поля, здесь нам не требуется
    приводить результат по модулю многочлена, задающего поля.
    Вместо этого при всех операциях лишь каждый коэффициент приводится по модулю p.
    """
    def __init__(self, coeffs, p):
        coeffs = self._trim_coeffs([int(c) % p for c in coeffs])

        self.poly = np.poly1d(coeffs)
        self.p = p

    @staticmethod
    def _trim_coeffs(coeffs):
        """
        Обрезает старшие нулевые коэффициенты (когда они пришли в результате выполнения операции других многочленов)
        """
        while len(coeffs) > 1 and coeffs[0] == 0:
            coeffs.pop(0)

        return coeffs

    def __add__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя складывать")
        
        coeffs1 = self.poly.coeffs
        coeffs2 = other.poly.coeffs

        max_len = max(len(coeffs1), len(coeffs2))

        coeffs1 = np.pad(coeffs1, (max_len - len(coeffs1), 0), 'constant')
        coeffs2 = np.pad(coeffs2, (max_len - len(coeffs2), 0), 'constant')

        result_coeffs = [(a + b) % self.p for a, b in zip(coeffs1, coeffs2)]

        return GaloisFieldSimplePolynom(result_coeffs, self.p)

    def __sub__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя вычитать")
        
        coeffs1 = self.poly.coeffs
        coeffs2 = other.poly.coeffs

        max_len = max(len(coeffs1), len(coeffs2))
        coeffs1 = np.pad(coeffs1, (max_len - len(coeffs1), 0), 'constant')
        coeffs2 = np.pad(coeffs2, (max_len - len(coeffs2), 0), 'constant')

        result_coeffs = [(a - b) % self.p for a, b in zip(coeffs1, coeffs2)]

        return GaloisFieldSimplePolynom(result_coeffs, self.p)

    def __mul__(self, other: 'GaloisFieldSimplePolynom') -> 'GaloisFieldSimplePolynom':
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя умножать")

        product_coeffs = karatsuba_multiply(self.poly.coeffs.tolist(), other.poly.coeffs.tolist(), self.p)

        product_coeffs = [c % self.p for c in product_coeffs]

        return GaloisFieldSimplePolynom(product_coeffs, self.p)

    def __truediv__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя делить")
        
        if np.all(other.poly.coeffs == 0):
            raise ZeroDivisionError("Деление на ноль.")
        
        quotient, remainder = np.polydiv(self.poly, other.poly)

        quotient_coeffs = [int(round(c)) % self.p for c in quotient.coeffs]
        remainder_coeffs = [int(round(c)) % self.p for c in remainder.coeffs]

        quotient_poly = GaloisFieldSimplePolynom(quotient_coeffs, self.p)
        remainder_poly = GaloisFieldSimplePolynom(remainder_coeffs, self.p)

        return quotient_poly, remainder_poly

    def __str__(self) -> str:
        return format_polynomial(self.poly)

    def calculate_value(self, element: GaloisFieldSimpleElement) -> GaloisFieldSimpleElement:
        """
        Вычисляет значение многочлена в данной точке
        """
        result = 0

        for coef in self.poly.coeffs:
            result = (result * element.value + coef) % self.p

        return GaloisFieldSimpleElement(result, self.p)
