class GaloisFieldSimpleElement:
    """
    Класс, представляющий собой элемент в простом поле GF(p).

    Для корректного и удобного выполнения операций с экземплярами данного класса,
    у него переопределены многие специальные методы (сложение, вычитание, умножение, деление).
    """
    def __init__(self, value, p):
        self.value = value % p
        self.p = p

    def __add__(self, other):
        if self.p != other.p:
            raise ValueError("Элементы из разных полей нельзя складывать")
        
        return GaloisFieldSimpleElement((self.value + other.value) % self.p, self.p)

    def __sub__(self, other):
        if self.p != other.p:
            raise ValueError("Элементы из разных полей нельзя вычитать")
        
        return GaloisFieldSimpleElement((self.value - other.value) % self.p, self.p)

    def __mul__(self, other):
        if self.p != other.p:
            raise ValueError("Элементы из разных полей нельзя умножать")
        
        return GaloisFieldSimpleElement((self.value * other.value) % self.p, self.p)

    def __truediv__(self, other):
        if self.p != other.p:
            raise ValueError("Элементы из разных полей нельзя делить")
        
        inverse = pow(other.value, -1, self.p)

        return GaloisFieldSimpleElement((self.value * inverse) % self.p, self.p)

    def inverse(self):
        inverse_value = pow(self.value, -1, self.p)

        return GaloisFieldSimpleElement(inverse_value, self.p)

    def __str__(self):
        return str(self.value)