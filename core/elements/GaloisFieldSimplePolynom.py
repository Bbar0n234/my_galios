import numpy as np
from .functions import format_polynomial
from .GaloisFieldSimpleElement import GaloisFieldSimpleElement


class GaloisFieldSimplePolynom:
    def __init__(self, coeffs, p):
        # Удаление ведущих нулей и приведение коэффициентов по модулю p
        coeffs = self._trim_coeffs([int(c) % p for c in coeffs])
        self.poly = np.poly1d(coeffs)
        self.p = p

    def _trim_coeffs(self, coeffs):
        # Удаление ведущих нулей
        while len(coeffs) > 1 and coeffs[0] == 0:
            coeffs.pop(0)
        return coeffs

    def __add__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя складывать")
        # Выравнивание длины коэффициентов
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
        # Выравнивание длины коэффициентов
        coeffs1 = self.poly.coeffs
        coeffs2 = other.poly.coeffs
        max_len = max(len(coeffs1), len(coeffs2))
        coeffs1 = np.pad(coeffs1, (max_len - len(coeffs1), 0), 'constant')
        coeffs2 = np.pad(coeffs2, (max_len - len(coeffs2), 0), 'constant')
        result_coeffs = [(a - b) % self.p for a, b in zip(coeffs1, coeffs2)]
        return GaloisFieldSimplePolynom(result_coeffs, self.p)

    def __mul__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя умножать")
        product = np.polymul(self.poly, other.poly)
        product_coeffs = [int(c) % self.p for c in product.coeffs]
        return GaloisFieldSimplePolynom(product_coeffs, self.p)

    def __truediv__(self, other):
        if self.p != other.p:
            raise ValueError("Многочлены из разных полей нельзя делить")
        if np.all(other.poly.coeffs == 0):
            raise ZeroDivisionError("Деление на ноль.")
        quotient, remainder = np.polydiv(self.poly, other.poly)
        # Приведение коэффициентов по модулю p
        quotient_coeffs = [int(round(c)) % self.p for c in quotient.coeffs]
        remainder_coeffs = [int(round(c)) % self.p for c in remainder.coeffs]
        quotient_poly = GaloisFieldSimplePolynom(quotient_coeffs, self.p)
        remainder_poly = GaloisFieldSimplePolynom(remainder_coeffs, self.p)
        return quotient_poly, remainder_poly

    def __str__(self):
        return format_polynomial(self.poly)

    def evaluate_at(self, element):
        # Оценка многочлена в элементе поля
        result = 0
        for coef in self.poly.coeffs:
            result = (result * element.value + coef) % self.p
        return GaloisFieldSimpleElement(result, self.p)
