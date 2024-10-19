
from elements import GaloisFieldSimpleElement, GaloisFieldSimplePolynom

class GaloisFieldSimple:
    """
    Класс, представляющий собой базовое поле GF(p).
    """
    def __init__(self, p):
        self.p = p

    def create_element(self, value):
        return GaloisFieldSimpleElement(value, self.p)
    
    def create_polynom(self, coeffs):
        return GaloisFieldSimplePolynom(coeffs, self.p)

    def __str__(self):
        return f"GF({self.p})"
