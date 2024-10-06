import streamlit as st
import numpy as np
from sympy import isprime
from core import GaloisField

# Функция для красивого отображения многочленов
def format_polynomial(poly: np.poly1d) -> str:
    """
    Преобразует многочлен из numpy.poly1d в читаемую строку.

    :param poly: Многочлен в формате numpy.poly1d.
    :return: Строка, представляющая многочлен.
    """
    coeffs = poly.coeffs
    degree = len(coeffs) - 1
    terms = []
    for i, coef in enumerate(coeffs):
        current_degree = degree - i
        coef = int(coef)
        if coef == 0:
            continue
        # Обработка коэффициента
        if abs(coef) == 1 and current_degree != 0:
            coef_str = "-" if coef == -1 else ""
        else:
            coef_str = str(coef)
        # Обработка степени
        if current_degree > 1:
            term = f"{coef_str}x^{current_degree}"
        elif current_degree == 1:
            term = f"{coef_str}x"
        else:
            term = f"{coef_str}"
        terms.append(term)
    if not terms:
        return "0"
    polynomial = " + ".join(terms)
    polynomial = polynomial.replace("+ -", "- ")
    return polynomial

# Заголовок приложения
st.title("Калькулятор поля Галуа GF(p^n)")

st.header("Определение поля")

# Ввод характеристики p
p = st.number_input("Введите характеристику p (простое число):", min_value=2, value=2, step=1)

# Ввод коэффициентов неприводимого многочлена
coeffs_input = st.text_input(
    "Введите коэффициенты неприводимого многочлена (от старшей степени к свободному члену), через запятую:",
    value="1,0,1"
)

# Парсинг коэффициентов
try:
    modulus_coeffs = [int(c.strip()) for c in coeffs_input.split(',')]
except ValueError:
    modulus_coeffs = None

# Инициализация состояния сессии
if 'field_p' not in st.session_state:
    st.session_state['field_p'] = None
if 'field_modulus_coeffs' not in st.session_state:
    st.session_state['field_modulus_coeffs'] = None
if 'polynomials' not in st.session_state:
    st.session_state['polynomials'] = {}
if 'last_operation_result' not in st.session_state:
    st.session_state['last_operation_result'] = None
if 'last_inverse_result' not in st.session_state:
    st.session_state['last_inverse_result'] = None
if 'last_evaluation_result' not in st.session_state:
    st.session_state['last_evaluation_result'] = None

# Проверка изменения поля
field_changed = False
if st.session_state['field_p'] != p or st.session_state['field_modulus_coeffs'] != modulus_coeffs:
    field_changed = True
    st.session_state['field_p'] = p
    st.session_state['field_modulus_coeffs'] = modulus_coeffs
    st.session_state['polynomials'] = {}  # Сброс элементов поля
    st.session_state['last_operation_result'] = None
    st.session_state['last_inverse_result'] = None
    st.session_state['last_evaluation_result'] = None

# Проверка простоты p и корректности многочлена
field = None
if modulus_coeffs is not None:
    if not isprime(p):
        st.error(f"{p} не является простым числом! Пожалуйста, введите простое число.")
    else:
        try:
            field = GaloisField(p, modulus_coeffs)
            st.success(f"Поле {field} успешно создано.")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Ошибка при создании поля.")
else:
    st.error("Пожалуйста, введите корректные целые числа, разделенные запятыми.")

if field:
    st.header("Элементы поля")

    # Ввод для добавления нового многочлена
    new_poly_input = st.text_input(
        "Введите коэффициенты нового элемента поля (от старшей степени к свободному члену), через запятую:",
        key="new_poly"
    )
    if st.button("Добавить элемент"):
        try:
            new_coeffs = [int(c.strip()) for c in new_poly_input.split(',')]
            element = field.create_element(new_coeffs)
            # Назначение уникального имени элементу
            element_id = len(st.session_state['polynomials']) + 1
            element_name = f"Элемент {element_id}"
            st.session_state['polynomials'][element_name] = element
            st.success(f"Добавлен {element_name}: {format_polynomial(element.poly)}")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Некорректный ввод коэффициентов многочлена.")

    # Отображение списка многочленов с возможностью удаления
    if st.session_state['polynomials']:
        st.subheader("Список элементов поля")
        for name, poly in st.session_state['polynomials'].items():
            cols = st.columns([4, 1])  # Создание колонок для отображения элемента и кнопки удаления
            with cols[0]:
                st.write(f"{name}: {format_polynomial(poly.poly)}")
            with cols[1]:
                if st.button("Удалить", key=f"del_{name}"):
                    del st.session_state['polynomials'][name]
                    st.success(f"{name} был удалён.")
                    st.rerun()  # Перезапуск приложения для обновления списка

        st.header("Операции")

        # Выбор двух элементов для операций
        element_names = list(st.session_state['polynomials'].keys())
        if len(element_names) < 2:
            st.info("Добавьте как минимум два элемента для выполнения операций.")
        else:
            el1_name = st.selectbox("Выберите первый элемент", element_names, key="el1")
            el2_name = st.selectbox("Выберите второй элемент", element_names, key="el2")

            el1 = st.session_state['polynomials'][el1_name]
            el2 = st.session_state['polynomials'][el2_name]

            # Выбор операции
            operation = st.selectbox("Выберите операцию", ["Сложение", "Вычитание", "Умножение", "Деление"])

            if st.button("Вычислить"):
                result = None
                try:
                    if operation == "Сложение":
                        result = el1 + el2
                    elif operation == "Вычитание":
                        result = el1 - el2
                    elif operation == "Умножение":
                        result = el1 * el2
                    elif operation == "Деление":
                        result = el1 / el2
                    if result:
                        st.session_state['last_operation_result'] = result
                        st.write(f"Результат: {format_polynomial(result.poly)}")
                except ZeroDivisionError:
                    st.error("Деление на ноль.")
                except Exception as e:
                    st.error(f"Ошибка при вычислении: {e}")

            # Кнопка для сохранения результата операции
            if st.session_state.get('last_operation_result') is not None:
                if st.button("Сохранить результат как новый элемент", key="save_result"):
                    result = st.session_state['last_operation_result']
                    element_id = len(st.session_state['polynomials']) + 1
                    element_name = f"Элемент {element_id}"
                    st.session_state['polynomials'][element_name] = result
                    st.success(f"Результат сохранен как {element_name}: {format_polynomial(result.poly)}")
                    st.session_state['last_operation_result'] = None  # Очистка после сохранения
                    st.rerun()

        st.header("Обратные элементы")

        st.subheader("Найти обратный элемент")
        el_inv_name = st.selectbox("Выберите элемент для нахождения обратного", element_names, key="el_inv")

        el_inv = st.session_state['polynomials'][el_inv_name]

        if st.button("Найти обратный"):
            try:
                inverse_el = el_inv.inverse()
                st.session_state['last_inverse_result'] = inverse_el
                st.write(f"Обратный элемент для {el_inv_name}: {format_polynomial(inverse_el.poly)}")
            except Exception as e:
                st.error("Этот элемент не имеет обратного.")

        # Кнопка для сохранения обратного элемента
        if st.session_state.get('last_inverse_result') is not None:
            if st.button("Сохранить обратный элемент как новый элемент", key="save_inverse"):
                inverse_el = st.session_state['last_inverse_result']
                element_id = len(st.session_state['polynomials']) + 1
                element_name = f"Элемент {element_id}"
                st.session_state['polynomials'][element_name] = inverse_el
                st.success(f"Обратный элемент сохранен как {element_name}: {format_polynomial(inverse_el.poly)}")
                st.session_state['last_inverse_result'] = None  # Очистка после сохранения
                st.rerun()

        st.header("Вычисление значений многочленов")

        st.subheader("Вычислить значение многочлена")
        el_eval_name = st.selectbox("Выберите элемент для вычисления", element_names, key="el_eval")
        el_eval = st.session_state['polynomials'][el_eval_name]
        x_value_input = st.text_input(
            "Введите значение для подстановки (коэффициенты многочлена через запятую):",
            key="x_value"
        )
        if st.button("Вычислить значение"):
            try:
                x_coeffs = [int(c.strip()) for c in x_value_input.split(',')]
                x_element = field.create_element(x_coeffs)
                result = el_eval.evaluate_at(x_element)
                st.session_state['last_evaluation_result'] = result
                st.write(f"Значение {format_polynomial(el_eval.poly)} при {format_polynomial(x_element.poly)}: {format_polynomial(result.poly)}")
            except Exception as e:
                st.error("Некорректный ввод значения для вычисления.")

        # # Кнопка для сохранения результата вычисления
        # if st.session_state.get('last_evaluation_result') is not None:
        #     if st.button("Сохранить результат как новый элемент", key="save_eval_result"):
        #         result = st.session_state['last_evaluation_result']
        #         element_id = len(st.session_state['polynomials']) + 1
        #         element_name = f"Элемент {element_id}"
        #         st.session_state['polynomials'][element_name] = result
        #         st.success(f"Результат сохранен как {element_name}: {format_polynomial(result.poly)}")
        #         st.session_state['last_evaluation_result'] = None  # Очистка после сохранения
        #         st.rerun()
    else:
        st.info("Пока нет добавленных элементов поля.")
