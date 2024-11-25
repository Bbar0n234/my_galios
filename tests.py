import os
import time

import pytest

from typing import List

from core import GaloisFieldSimple, GaloisFieldExtension

from sage.all import *


def normalize_coeffs(coeffs: List[int]) -> List[int]:
    """
    Нормализует список коэффициентов: если все коэффициенты равны 0, возвращает пустой список.
    Иначе возвращает исходный список.
    
    :param coeffs: Список коэффициентов многочлена.
    :return: Нормализованный список коэффициентов.
    """
    if all(coef == 0 for coef in coeffs):
        return []
    return coeffs


def log_timing(degree: int, elapsed_time: float, filename: str = "timing_results_extension.txt"):
    """
    Записывает степень многочлена и время выполнения в указанный файл.

    :param degree: Степень многочлена.
    :param elapsed_time: Время выполнения в секундах.
    :param filename: Имя файла для записи результатов.
    """
    with open(filename, 'a') as f:
        f.write(f"{degree},{elapsed_time}\n")


test_data_simple = {
    "simple_elements": [
        {"field": 5, "a": 3, "b": 4, "Ожидалось_sum": 2, "Ожидалось_mul": 2},
        {"field": 7, "a": 2, "b": 5, "Ожидалось_sum": 0, "Ожидалось_mul": 3},
    ],
    "polynomials": [
        {
            "field": 3,
            "P": [1, 2, 0, 1],
            "Q": [1, 2, 1],
            "eval_point": 2,
        },
        {
            "field": 2,
            "P": [1, 1, 1, 1],
            "Q": [1, 0, 1],
            "eval_point": 1,
        },
    ]

}

test_data_extension = [
    {
        "field": 3,
        "modulus": [1, 0, 1],
        "a_coeffs": [1, 1],  
        "b_coeffs": [1, 1],   
    },
    {
        "field": 2,
        "modulus": [1, 1, 1],  
        "a_coeffs": [1, 0],   
        "b_coeffs": [1, 1],    
    },
    {
        "field": 3,
        "modulus": [1, 1, 2],  
        "a_coeffs": [2, 0],    
        "b_coeffs": [1, 2],    
    },

        {
        "field": 3,
        "modulus": [2, 1, 1, 1], 
        "a_coeffs": [2, 1],     
        "b_coeffs": [1, 2, 1],    
    },  
    {
        "field": 2,
        "modulus": [1, 1, 0, 1], 
        "a_coeffs": [1, 1, 1],     
        "b_coeffs": [1, 0, 1],    
    },
    {
        "field": 2,
        "modulus": [1, 1, 0, 1],  
        "a_coeffs": [1, 0, 1],     
        "b_coeffs": [1, 1, 0],     
    },

    {
        "field": 5,
        "modulus": [1, 2, 0, 1], 
        "a_coeffs": [3, 4, 1], 
        "b_coeffs": [1, 0, 2], 
    },
    {
        "field": 5,
        "modulus": [1, 0, 4, 2],
        "a_coeffs": [1, 0, 1],
        "b_coeffs": [2, 3, 1],
    },
    {
        "field": 5,
        "modulus": [1, 0, 1, 3, 2],
        "a_coeffs": [1, 2, 3, 1],
        "b_coeffs": [2, 3, 1, 4],
    },
    {
        "field": 5,
        "modulus": [1, 0, 1, 4, 1],
        "a_coeffs": [4, 2, 5, 1],
        "b_coeffs": [6, 1, 3, 2],
    },

    {
        "field": 7,
        "modulus": [1, 4, 1],
        "a_coeffs": [4, 5],
        "b_coeffs": [2, 6],
    },
    {
        "field": 7,
        "modulus": [1, 0, 6, 2],
        "a_coeffs": [3, 2, 5],
        "b_coeffs": [1, 4, 3],
    },
    {
        "field": 7,
        "modulus": [1, 0, 1, 1, 1],
        "a_coeffs": [2, 1, 0, 4],
        "b_coeffs": [5, 2, 3, 4],
    },
    # Тесты на огромных значениях
    {
        "field": 2,
        "modulus": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1],
        "a_coeffs": [1, 1, 0, 1,1, 1, 0, 1,1, 1, 0, 1,1, 1, 0, 1,1, 1, 0, 1,],
        "b_coeffs": [1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,],  
    },
    {
        "field": 2,
        "modulus": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1],
        "a_coeffs": [1, 1, 0, 1,1, 1, 0, 1,1, 1, 0, 0,0,1,1, 1,1, 1, 0, 1,1, 1, 0, 1,],
        "b_coeffs": [1, 0,0,1,1, 0, 1, 0, 1,1, 1, 0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,1, 0,0,1,],  
    },
    {
        "field": 3,
        "modulus": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2],
        "a_coeffs": [1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1,],
        "b_coeffs": [1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2],  
    },

    {
        "field": 3,
        "modulus": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1],
        "a_coeffs": [2, 2, 1, 0, 2, 2, 1, 0, 2, 2, 1, 0, 2, 2, 1, 0,],
        "b_coeffs": [1, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0],  
    },

    {
        "field": 5,
        "modulus": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 3, 1],
        "a_coeffs": [4, 3, 2, 4, 4, 3, 2, 4, 4, 3, 2, 4, 4, 3, 2, 4,],
        "b_coeffs": [2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4],  
    },
]


# Тесты для обычных элементов простого поля
@pytest.mark.parametrize("data", test_data_simple["simple_elements"])
def test_galois_simple_elems(data):
    gf = GaloisFieldSimple(data["field"])
    a = gf.create_element(data["a"])
    b = gf.create_element(data["b"])

    sum_result = a + b
    sum_value = sum_result.value
    sum_value = [] if sum_value == [0] else sum_value  # Обработка [0] -> []
    assert sum_value == data["Ожидалось_sum"], f"Ожидалось {data['Ожидалось_sum']}, получено {sum_value}"

    mul_result = a * b
    mul_value = mul_result.value
    mul_value = [] if mul_value == [0] else mul_value  # Обработка [0] -> []
    assert mul_value == data["Ожидалось_mul"], f"Ожидалось {data['Ожидалось_mul']}, получено {mul_value}"


# Тесты для многочленов простого поля
@pytest.mark.parametrize("data", test_data_simple["polynomials"])
def test_galois_simple_polys(data):
    p = data['field']

    F = GF(p)
    GF_simple = GaloisFieldSimple(p)

    # Определяем полиномное кольцо над F_p
    R = PolynomialRing(F, 'x')
    x = R.gen()

    P_coeffs = data['P']
    Q_coeffs = data['Q']

    P_sage = R(P_coeffs[::-1])
    Q_sage = R(Q_coeffs[::-1])
    
    P_my = GF_simple.create_polynom(P_coeffs)
    Q_my = GF_simple.create_polynom(Q_coeffs)

    # Сложение
    my_sum_result = P_my + Q_my
    my_sum_coeffs = list(my_sum_result.poly.coefficients.tolist())
    my_sum_coeffs = normalize_coeffs(my_sum_coeffs)

    sage_sum_result = P_sage + Q_sage
    sage_sum_coeffs = list(sage_sum_result.list()[::-1])
    sage_sum_coeffs = normalize_coeffs(sage_sum_coeffs)

    assert my_sum_coeffs == sage_sum_coeffs, f"Ожидалось {sage_sum_coeffs}, получено {my_sum_coeffs}"

    # Вычитание
    my_sub_result = P_my - Q_my
    my_sub_coeffs = list(my_sub_result.poly.coefficients.tolist())
    my_sub_coeffs = normalize_coeffs(my_sub_coeffs)
    
    sage_sub_result = P_sage - Q_sage
    sage_sub_coeffs = list(sage_sub_result.list()[::-1])
    sage_sub_coeffs = normalize_coeffs(sage_sub_coeffs)

    assert my_sub_coeffs == sage_sub_coeffs, f"Ожидалось {sage_sub_coeffs}, получено {my_sub_coeffs}"

    # Умножение
    my_mul_result = P_my * Q_my
    my_mul_coeffs = list(my_mul_result.poly.coefficients.tolist())
    my_mul_coeffs = normalize_coeffs(my_mul_coeffs)
    
    sage_mul_result = P_sage * Q_sage
    sage_mul_coeffs = list(sage_mul_result.list()[::-1])
    sage_mul_coeffs = normalize_coeffs(sage_mul_coeffs)

    assert my_mul_coeffs == sage_mul_coeffs, f"Ожидалось {sage_mul_coeffs}, получено {my_mul_coeffs}"

    # Деление
    my_div_result, my_remainder = P_my / Q_my
    my_div_coeffs = list(my_div_result.poly.coefficients.tolist())
    my_remainder_coeffs = list(my_remainder.poly.coefficients.tolist())

    my_div_coeffs = normalize_coeffs(my_div_coeffs)
    my_remainder_coeffs = normalize_coeffs(my_remainder_coeffs)

    sage_div_result, sage_remainder = P_sage.quo_rem(Q_sage)
    sage_div_coeffs = list(sage_div_result.list()[::-1])
    sage_rem_coeffs = list(sage_remainder.list()[::-1])

    sage_div_coeffs = normalize_coeffs(sage_div_coeffs)
    sage_rem_coeffs = normalize_coeffs(sage_rem_coeffs)

    assert my_div_coeffs == sage_div_coeffs, \
        f"Ожидалось {sage_div_coeffs}, получено {my_div_coeffs}"

    assert my_remainder_coeffs == sage_rem_coeffs, \
        f"Ожидалось {sage_rem_coeffs}, получено {my_remainder_coeffs}"

    # Вычисление значения в заданной точке
    eval_point = data['eval_point']

    sage_eval_point = F(eval_point)
    my_eval_point = GF_simple.create_element(eval_point)

    sage_eval_P = P_sage(eval_point)
    sage_eval_Q = Q_sage(sage_eval_point)

    my_eval_P = P_my.calculate_value(my_eval_point).value
    my_eval_Q = Q_my.calculate_value(my_eval_point).value


    assert sage_eval_P == my_eval_P, f"Ожидалось {sage_eval_P}, получено {my_eval_P}"
    assert sage_eval_Q == my_eval_Q, f"Ожидалось {sage_eval_Q}, получено {my_eval_Q}"


@pytest.mark.parametrize("data", test_data_extension)
def test_galois_field_extension(data):
    # Инициализация поля в Sage
    p = data["field"]
    modulus_coeffs = data["modulus"]

    F = GF(p)
    R = PolynomialRing(F, 'x')
    x = R.gen()
    sage_field = GF(p**(len(modulus_coeffs) - 1), name="a", modulus=R(modulus_coeffs[::-1]))

    # Инициализация поля в нашем коде
    gf_extension = GaloisFieldExtension(p, modulus_coeffs)
    a = gf_extension.create_element(data["a_coeffs"])
    b = gf_extension.create_element(data["b_coeffs"])

    # Создание Sage элементов
    sage_a = sage_field(data["a_coeffs"][::-1])
    sage_b = sage_field(data["b_coeffs"][::-1])

        # Определение степени многочленов
    degree_a = len(data["a_coeffs"]) - 1
    degree_b = len(data["b_coeffs"]) - 1
    max_degree = max(degree_a, degree_b)

    # Начало замера времени
    start_time = time.perf_counter()

    # Сложение
    my_sum_result = a + b
    my_sum_coeffs = list(my_sum_result.poly.coefficients.tolist())
    my_sum_coeffs = normalize_coeffs(my_sum_coeffs)

    sage_sum_result = sage_a + sage_b
    sage_sum_coeffs = list(sage_sum_result.polynomial().coefficients(sparse=False)[::-1])
    sage_sum_coeffs = normalize_coeffs(sage_sum_coeffs)

    assert my_sum_coeffs == sage_sum_coeffs, f"Ожидалось {sage_sum_coeffs}, получено {my_sum_coeffs}"

    # Вычитание
    my_sub_result = a - b
    my_sub_coeffs = list(my_sub_result.poly.coefficients.tolist())
    my_sub_coeffs = normalize_coeffs(my_sub_coeffs)
    
    sage_sub_result = sage_a - sage_b
    sage_sub_coeffs = list(sage_sub_result.polynomial().coefficients(sparse=False)[::-1])
    sage_sub_coeffs = normalize_coeffs(sage_sub_coeffs)

    assert my_sub_coeffs == sage_sub_coeffs, f"Ожидалось {sage_sub_coeffs}, получено {my_sub_coeffs}"

    # Умножение
    my_mul_result = a * b
    my_mul_coeffs = list(my_mul_result.poly.coefficients.tolist())
    my_mul_coeffs = normalize_coeffs(my_mul_coeffs)
    
    sage_mul_result = sage_a * sage_b
    sage_mul_coeffs = list(sage_mul_result.polynomial().coefficients(sparse=False)[::-1])
    sage_mul_coeffs = normalize_coeffs(sage_mul_coeffs)

    assert my_mul_coeffs == sage_mul_coeffs, f"Ожидалось {sage_mul_coeffs}, получено {my_mul_coeffs}"

 # Деление
    if data["a_coeffs"] != data["b_coeffs"]:  # Деление на равные элементы не имеет смысла
        sage_div_result = sage_a / sage_b
        sage_div_coeffs = list(sage_div_result.polynomial().coefficients(sparse=False)[::-1])

        my_div_result = a / b
        my_div_coeffs = list(my_div_result.poly.coefficients.tolist())

        assert my_div_coeffs == sage_div_coeffs, f"Ожидалось {sage_div_coeffs}, получено {my_div_coeffs}"

    # Нахождение обратного элемента
    if list(b.poly.coeffs) != [0]:  # Проверяем, что b не равно нулю
        my_inv_result = b.inverse()
        my_inv_coeffs = list(my_inv_result.poly.coefficients.tolist())
        my_inv_coeffs = normalize_coeffs(my_inv_coeffs)

        sage_inv_result = sage_b.inverse()
        sage_inv_coeffs = list(sage_inv_result.polynomial().coefficients(sparse=False)[::-1])
        sage_inv_coeffs = normalize_coeffs(sage_inv_coeffs)

        assert my_inv_coeffs == sage_inv_coeffs, f"Ожидалось {sage_inv_coeffs}, получено {my_inv_coeffs}"

    # Конец замера времени
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # Логирование результатов
    log_timing(max_degree, elapsed_time)
