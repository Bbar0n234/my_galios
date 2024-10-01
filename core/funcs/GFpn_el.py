from __future__ import annotations

import numpy as np

from typing import List


def modulus_coeffs(coeffs, p):
    """
    Считает каждый коэффицент многочлена по модулю p
    """
    # if isinstance(coeffs, Fpn):
    #     return coeffs % p

    if not isinstance(coeffs, int):
        return coeffs % p

    return np.array([el % p for el in coeffs], int)


def modulus_poly(poly1: np.poly1d, poly2: np.poly1d, p: int):
    """
    Берёт многочлен по модулю другого многочлена
    """
    _, r = np.polydiv(poly1, poly2)
    coeffs = modulus_coeffs(r.coeffs, p) 
    # coeffs = np.mod(r.coeffs, p)

    return np.poly1d(coeffs)


def modulus_pow_poly(poly: np.poly1d, e: int, p: int, mod_poly: np.poly1d) -> np.poly1d:
    result = np.poly1d([1])
    base = np.poly1d(poly.coeffs) 

    exponent_mod = p ** (len(mod_poly.coeffs) - 1) - 1
    e = e % exponent_mod
    if e == 0:
        return result

    while e > 0:
        if e % 2 == 1:
            result = modulus_poly(result * base, mod_poly, p)
        base = modulus_poly(base * base, mod_poly, p)
        e = e // 2

    return result



def inverse_element(el, p):
    """
    Считает обратный элемент в поле F(p)
    """
    return pow(int(el), p-2, p)


def inverse_poly(poly, p, mod_poly):
    """
    Считает обратный элемент в поле F(p^n)
    """
    if len(poly.coeffs) == 1:
        inverse_of_el = inverse_element(poly.coeffs[0], p)
        return np.poly1d(np.array([inverse_of_el]))
    
    return modulus_pow_poly(poly, p**(len(mod_poly.coeffs)-1)-2, p, mod_poly) # Возводим многочлен в степень p^n-2, т.е. это даст обратный элемент


class GfpnEl:
    """
    Класс, представляющий собой элемент (многочлен) в поле GF(p^n).
    """
    def __init__(self, p: int, coeffs:List[int], mod_poly: np.poly1d):
        self.p = p
        self.mod_poly = mod_poly

        _, r = np.polydiv(np.poly1d(coeffs), mod_poly) # сразу приводится по модулю многочлена

        self.poly = np.poly1d([coef % p for coef in r])


    def calc_poly_values(self, x):
        result = np.poly1d([0])
        x_pow = np.poly1d([1])

        for coeff in self.poly.coeffs[::-1]:
            term = coeff * x_pow

            result = modulus_poly(result + term, self.mod_poly, self.p)

            x_pow = modulus_poly(x_pow * x, self.mod_poly, self.p)

        return result
    

    def __repr__(self) -> str:
        def c2str(array): return str(list(array))
        mod_str = c2str(self.mod_poly.coeffs)
        return f'GfpnEl({c2str(list(map(int, self.poly.coeffs)))}, {self.p}, {mod_str})'


    def __add__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = self.poly + other.poly
        else:
            result = self.poly + other
        
        return GfpnEl(self.p, result.coeffs , self.mod_poly)
    

    def __radd__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = other.poly + self.poly
        else:
            result = other + self.poly
        
        return GfpnEl(self.p, result.coeffs , self.mod_poly)
    

    def __sub__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = self.poly - other.poly
        else:
            result = self.poly - other
        
        return GfpnEl(self.p, result.coeffs , self.mod_poly)
    

    def __rsub__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = other.poly - self.poly
        else:
            result = other - self.poly
        
        return GfpnEl(self.p, result.coeffs , self.mod_poly)
    

    def __mul__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = self.poly * other.poly
        else:
            result = self.poly * other

        return GfpnEl(self.p, result.coeffs, self.mod_poly)
    

    def __rmul__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = other.poly * self.poly
        else:
            result = other * self.poly

        return GfpnEl(self.p, result.coeffs, self.mod_poly)
    

    def __truediv__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = self.poly * inverse_poly(other.poly, self.p, self.mod_poly) 
        else:
            result = self.poly * inverse_element(other, self.p, self.mod_poly)

        return GfpnEl(self.p, result.coeffs, self.mod_poly)
    

    def __rtruediv__(self, other: GfpnEl) -> GfpnEl:
        if isinstance(other, GfpnEl):
            result = other.poly * inverse_poly(self.poly,  self.p, self.mod_poly)
        else:
            result = other * inverse_poly(self.poly, self.p, self.mod_poly)

        return GfpnEl(self.p, result.coeffs, self.mod_poly)
    
    def inverse(self):
        inv_poly = inverse_poly(self.poly, self.p, self.mod_poly)
        return GfpnEl(self.p, inv_poly.coeffs, self.mod_poly)
