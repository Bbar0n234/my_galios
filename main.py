import numpy as np
from core import GFpn

my_field = GFpn(5, [1, 0, 0, 0, 2]) # Создаётся поле x^5 + 2 

el_1 = my_field.create_el([1, 2])

el_2 = my_field.create_el([1, 2, 3, 4, 5])

new_el = el_1 + el_2

print(el_1.calc_poly_values(0))

# The Inverse of elements.
print(el_1.inverse()) # 3x^3 + 4x^2 + 2x + 1
print(el_2.inverse()) # 1x^3 + 1x^2 + 2x + 1