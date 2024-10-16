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

# Функция для добавления записи операции в лог
def log_operation(operation_log, entry):
    operation_log.append(entry)
    st.session_state['operation_log'] = operation_log

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
if 'operation_log' not in st.session_state:
    st.session_state['operation_log'] = []

# Заголовок приложения
st.title("Калькулятор поля Галуа GF(p^n)")

st.header("Определение поля")

# Ввод характеристики p
p = st.number_input("Введите характеристику p (простое число):", min_value=2, value=2, step=1)

# Проверка простоты p
if not isprime(p):
    st.error(f"{p} не является простым числом! Пожалуйста, введите простое число.")
    p = None

# Ввод коэффициентов неприводимого многочлена
coeffs_input = st.text_input(
    "Введите коэффициенты неприводимого многочлена (от старшей степени к свободному члену), через запятую:",
    value="1,0,1"
)
modulus_file = st.file_uploader("Или загрузите коэффициенты из файла:", type=["txt"], key="modulus_file")

if modulus_file is not None:
    try:
        coeffs_input = modulus_file.read().decode('utf-8')
    except Exception as e:
        st.error("Ошибка при чтении файла с коэффициентами неприводимого многочлена.")

# Парсинг коэффициентов
try:
    modulus_coeffs = [int(c.strip()) % p for c in coeffs_input.split(',')] if p else None
except ValueError:
    modulus_coeffs = None

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

# Проверка корректности многочлена и создания поля
field = None
if modulus_coeffs is not None and p:
    if len(modulus_coeffs) < 2:
        st.error("Многочлен должен иметь степень как минимум 1 (введите как минимум два коэффициента).")
    else:
        try:
            field = GaloisField(p, modulus_coeffs)
            st.success(f"Поле {field} успешно создано.")

            st.write("**Многочлен, задающий поле:**")
            st.write(format_polynomial(field.modulus_polynomial))
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Ошибка при создании поля.")
else:
    if modulus_coeffs is None:
        st.error("Пожалуйста, введите корректные целые числа для коэффициентов неприводимого многочлена.")
    else:
        st.info("Пожалуйста, введите корректную характеристику поля p.")

if field:
    st.header("Элементы поля")

    # Ввод для добавления нового многочлена
    new_poly_input = st.text_input(
        "Введите коэффициенты нового элемента поля (от старшей степени к свободному члену), через запятую:",
        key="new_poly"
    )
    new_poly_file = st.file_uploader("Или загрузите коэффициенты элемента из файла:", type=["txt"], key="new_poly_file")

    if new_poly_file is not None:
        try:
            new_poly_input = new_poly_file.read().decode('utf-8')
        except Exception as e:
            st.error("Ошибка при чтении файла с коэффициентами элемента.")

    if st.button("Добавить элемент"):
        try:
            new_coeffs = [int(c.strip()) % p for c in new_poly_input.split(',')]
            if len(new_coeffs) > len(field.modulus_polynomial.coeffs) - 1:
                st.warning(f"Максимальная степень элемента поля: {len(field.modulus_polynomial.coeffs) - 2}. Привожу многочлен по модулю.")
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
                        # Логирование операции
                        entry = f"Операция: {operation}\nПоле: GF({p}^{field.n})\n{el1_name}: {format_polynomial(el1.poly)}\n{el2_name}: {format_polynomial(el2.poly)}\nРезультат: {format_polynomial(result.poly)}\n"
                        log_operation(st.session_state['operation_log'], entry)
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
                # Логирование операции
                entry = f"Операция: Нахождение обратного элемента\nПоле: GF({p}^{len(field.modulus_polynomial.coeffs) - 1})\nЭлемент: {format_polynomial(el_inv.poly)}\nОбратный элемент: {format_polynomial(inverse_el.poly)}\n"
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                print(e)
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
        x_value_file = st.file_uploader("Или загрузите значение для подстановки из файла:", type=["txt"], key="x_value_file")

        if x_value_file is not None:
            try:
                x_value_input = x_value_file.read().decode('utf-8')
            except Exception as e:
                st.error("Ошибка при чтении файла со значением для подстановки.")

        if st.button("Вычислить значение"):
            try:
                # При вычислении значения многочлена
                x_coeffs = [int(c.strip()) % p for c in x_value_input.split(',')]
                if len(x_coeffs) > len(field.modulus_polynomial.coeffs) - 1:
                    st.warning(f"Максимальная степень элемента поля: {len(field.modulus_polynomial.coeffs) - 2}. Привожу многочлен по модулю.")
                x_element = field.create_element(x_coeffs)
                result = el_eval.evaluate_at(x_element)
                st.session_state['last_evaluation_result'] = result
                st.write(f"Значение {format_polynomial(el_eval.poly)} при {format_polynomial(x_element.poly)}: {format_polynomial(result.poly)}")
                # Логирование операции
                entry = f"Операция: Вычисление значения многочлена\nПоле: GF({p}^{field.n})\nМногочлен: {format_polynomial(el_eval.poly)}\nЗначение: {format_polynomial(x_element.poly)}\nРезультат: {format_polynomial(result.poly)}\n"
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error("Некорректный ввод значения для вычисления.")
    else:
        st.info("Пока нет добавленных элементов поля.")

# Новый раздел для операций с многочленами над GF(p)
st.header("Операции с многочленами над GF(p)")

if p:
    st.subheader("Ввод многочленов")

    # Ввод первого многочлена
    poly1_input = st.text_input("Введите коэффициенты первого многочлена (от старшей степени к свободному члену), через запятую:", key="poly1_input")
    poly1_file = st.file_uploader("Или загрузите коэффициенты первого многочлена из файла:", type=["txt"], key="poly1_file")

    if poly1_file is not None:
        try:
            poly1_input = poly1_file.read().decode('utf-8')
        except Exception as e:
            st.error("Ошибка при чтении файла с первым многочленом.")

    # Ввод второго многочлена
    poly2_input = st.text_input("Введите коэффициенты второго многочлена (от старшей степени к свободному члену), через запятую:", key="poly2_input")
    poly2_file = st.file_uploader("Или загрузите коэффициенты второго многочлена из файла:", type=["txt"], key="poly2_file")

    if poly2_file is not None:
        try:
            poly2_input = poly2_file.read().decode('utf-8')
        except Exception as e:
            st.error("Ошибка при чтении файла со вторым многочленом.")

    # Парсинг коэффициентов
    try:
        poly1_coeffs = [int(c.strip()) % p for c in poly1_input.split(',')]
        poly1 = np.poly1d(poly1_coeffs)
        st.write("Первый многочлен:")
        st.write(format_polynomial(poly1))
    except Exception as e:
        poly1 = None
        st.error("Некорректный ввод для первого многочлена.")

    try:
        poly2_coeffs = [int(c.strip()) % p for c in poly2_input.split(',')]
        poly2 = np.poly1d(poly2_coeffs)
        st.write("Второй многочлен:")
        st.write(format_polynomial(poly2))
    except Exception as e:
        poly2 = None
        st.error("Некорректный ввод для второго многочлена.")

    if poly1 is not None and poly2 is not None:
        # Выбор операции
        operation = st.selectbox("Выберите операцию", ["Сложение", "Вычитание", "Умножение", "Деление"], key="poly_operation")

        if st.button("Выполнить операцию", key="compute_poly_operation"):
            result = None
            try:
                if operation == "Сложение":
                    result_coeffs = (np.polyadd(poly1, poly2).coeffs % p).astype(int)
                    result = np.poly1d(result_coeffs)
                elif operation == "Вычитание":
                    result_coeffs = (np.polysub(poly1, poly2).coeffs % p).astype(int)
                    result = np.poly1d(result_coeffs)
                elif operation == "Умножение":
                    result_coeffs = (np.polymul(poly1, poly2).coeffs % p).astype(int)
                    result = np.poly1d(result_coeffs)
                elif operation == "Деление":
                    if np.all(poly2.coeffs == 0):
                        st.error("Деление на ноль.")
                    else:
                        # Выполняем деление с остатком
                        quotient, remainder = np.polydiv(poly1, poly2)
                        quotient_coeffs = (np.round(quotient).astype(int) % p).astype(int)
                        remainder_coeffs = (np.round(remainder).astype(int) % p).astype(int)
                        quotient_poly = np.poly1d(quotient_coeffs)
                        remainder_poly = np.poly1d(remainder_coeffs)
                        st.write(f"Частное: {format_polynomial(quotient_poly)}")
                        st.write(f"Остаток: {format_polynomial(remainder_poly)}")
                        # Логирование операции
                        entry = f"Операция: {operation}\nПоле: GF({p})\nПервый многочлен: {format_polynomial(poly1)}\nВторой многочлен: {format_polynomial(poly2)}\nЧастное: {format_polynomial(quotient_poly)}\nОстаток: {format_polynomial(remainder_poly)}\n"
                        log_operation(st.session_state['operation_log'], entry)
                        result = None  # Результат уже выведен
                if result is not None:
                    st.write(f"Результат: {format_polynomial(result)}")
                    # Логирование операции
                    entry = f"Операция: {operation}\nПоле: GF({p})\nПервый многочлен: {format_polynomial(poly1)}\nВторой многочлен: {format_polynomial(poly2)}\nРезультат: {format_polynomial(result)}\n"
                    log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error(f"Ошибка при выполнении операции: {e}")
else:
    st.info("Пожалуйста, введите корректную характеристику поля p.")

        # Кнопка для скачивания лога операций
if st.session_state['operation_log']:
    operation_log_str = "\n".join(st.session_state['operation_log'])
    st.download_button("Скачать лог операций", operation_log_str, file_name="operation_log.txt")
