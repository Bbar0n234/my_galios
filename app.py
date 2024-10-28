import os

import streamlit as st

from sympy import isprime


from core import GaloisFieldExtension, GaloisFieldSimple
from core import format_polynomial


# Функция для добавления записи в лог
def log_operation(operation_log, entry):
    operation_log.append(entry)
    st.session_state['operation_log'] = operation_log


# Инициализация состояния сессии
if 'field_type' not in st.session_state:
    st.session_state['field_type'] = 'Расширение поля'
if 'field_p' not in st.session_state:
    st.session_state['field_p'] = None
if 'field_modulus_coeffs' not in st.session_state:
    st.session_state['field_modulus_coeffs'] = None
if 'field_elements_simple' not in st.session_state:
    st.session_state['field_elements_simple'] = {}
if 'polynomials_simple' not in st.session_state:
    st.session_state['polynomials_simple'] = {}
if 'polynomials_poly_simple' not in st.session_state:
    st.session_state['polynomials_poly_simple'] = {}
if 'last_operation_result_element' not in st.session_state:
    st.session_state['last_operation_result_element'] = None
if 'last_operation_result_polynomial' not in st.session_state:
    st.session_state['last_operation_result_polynomial'] = None
if 'last_inverse_result_element' not in st.session_state:
    st.session_state['last_inverse_result_element'] = None
if 'last_inverse_result_polynomial' not in st.session_state:
    st.session_state['last_inverse_result_polynomial'] = None
if 'last_evaluation_result' not in st.session_state:
    st.session_state['last_evaluation_result'] = None
if 'operation_log' not in st.session_state:
    st.session_state['operation_log'] = []

st.title("Калькулятор поля Галуа GF(p^n)")

field_type = st.radio("Выберите тип поля", ('Расширение поля', 'Простое поле'))
st.session_state['field_type'] = field_type

st.header("Определение поля")

p = st.number_input("Введите характеристику p (простое число):", min_value=2, value=2, step=1)

if not isprime(p):
    st.error(f"{p} не является простым числом! Пожалуйста, введите простое число.")
    p = None

field = None

if field_type == 'Расширение поля':
    coeffs_input = st.text_input(
        "Введите коэффициенты неприводимого многочлена (от старшей степени к младшей), через запятую:",
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
    if (st.session_state['field_p'] != p or st.session_state['field_modulus_coeffs'] != modulus_coeffs or
            st.session_state['field_type'] != field_type):
        field_changed = True
        st.session_state['field_p'] = p
        st.session_state['field_modulus_coeffs'] = modulus_coeffs
        st.session_state['field_type'] = field_type
        st.session_state['field_elements_simple'] = {}
        st.session_state['polynomials_simple'] = {}
        st.session_state['polynomials_poly_simple'] = {}
        st.session_state['last_operation_result_element'] = None
        st.session_state['last_operation_result_polynomial'] = None
        st.session_state['last_inverse_result_element'] = None
        st.session_state['last_inverse_result_polynomial'] = None
        st.session_state['last_evaluation_result'] = None

    if modulus_coeffs is not None and p:
        if len(modulus_coeffs) < 3:
            st.error("Многочлен должен иметь степень как минимум 2 (введите как минимум 3 коэффициента).")
        else:
            try:
                field = GaloisFieldExtension(p, modulus_coeffs)
                st.success(f"Поле {field} успешно создано.")

                st.write("**Многочлен, задающий поле:**")
                st.write(format_polynomial(field.modulus_polynomial))
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error("Ошибка при создании поля.")
    else:
        if modulus_coeffs is None and p:
            st.error("Пожалуйста, введите корректные целые числа для коэффициентов неприводимого многочлена.")
        elif p is None:
            st.info("Пожалуйста, введите корректную характеристику поля p.")

elif field_type == 'Простое поле':
    modulus_coeffs = None
    field_changed = False
    if (st.session_state['field_p'] != p or st.session_state['field_modulus_coeffs'] != modulus_coeffs or
            st.session_state['field_type'] != field_type):
        field_changed = True
        st.session_state['field_p'] = p
        st.session_state['field_modulus_coeffs'] = modulus_coeffs
        st.session_state['field_type'] = field_type
        st.session_state['field_elements_simple'] = {}
        st.session_state['polynomials_simple'] = {}
        st.session_state['polynomials_poly_simple'] = {}
        st.session_state['last_operation_result_element'] = None
        st.session_state['last_operation_result_polynomial'] = None
        st.session_state['last_inverse_result_element'] = None
        st.session_state['last_inverse_result_polynomial'] = None
        st.session_state['last_evaluation_result'] = None

    if p:
        field = GaloisFieldSimple(p)
        st.success(f"Поле {field} успешно создано.")
    else:
        st.info("Пожалуйста, введите корректную характеристику поля p.")

if field:
    st.header("Элементы поля")

    if field_type == 'Расширение поля':
        new_poly_input = st.text_input(
            "Введите коэффициенты нового элемента поля (от старшей степени к свободному члену), через запятую:",
            key="new_poly"
        )
        new_poly_file = st.file_uploader("Или загрузите коэффициенты элемента из файла:", type=["txt"],
                                         key="new_poly_file")

        if new_poly_file is not None:
            try:
                new_poly_input = new_poly_file.read().decode('utf-8')
            except Exception as e:
                st.error("Ошибка при чтении файла с коэффициентами элемента.")

        if st.button("Добавить элемент"):
            try:
                new_coeffs = [int(c.strip()) % p for c in new_poly_input.split(',')]

                if len(new_coeffs) > len(field.modulus_polynomial.coeffs) - 1:
                    st.warning(
                        f"Максимальная степень элемента поля: {len(field.modulus_polynomial.coeffs) - 2}. Привожу многочлен по модулю.")
                element = field.create_element(new_coeffs)

                element_name = format_polynomial(element.poly)

                st.session_state['field_elements_simple'][element_name] = element
                st.success(f"Добавлен элемент {format_polynomial(element.poly)}")

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error("Некорректный ввод коэффициентов многочлена.")
    else:
        new_element_value = st.number_input("Введите значение нового элемента поля:", step=1, key="new_element")

        if st.button("Добавить элемент"):
            try:
                element = field.create_element(new_element_value)

                element_name = element.value


                st.session_state['field_elements_simple'][element_name] = element
                st.success(f"Добавлен элемент {element.value}")
            except Exception as e:
                st.error("Ошибка при добавлении элемента.")

    if field_type == 'Расширение поля' and st.session_state['field_elements_simple']:
        st.subheader("Список элементов поля")
        for name, element in st.session_state['field_elements_simple'].items():
            cols = st.columns([4, 1])
            with cols[0]:
                st.write(f"{format_polynomial(element.poly)}")
            with cols[1]:
                if st.button("Удалить", key=f"del_{name}"):
                    del st.session_state['field_elements_simple'][name]
                    st.success(f"{name} был удалён.")
                    st.rerun()
    elif field_type == 'Простое поле' and st.session_state['field_elements_simple']:
        st.subheader("Список элементов поля")
        for name, element in st.session_state['field_elements_simple'].items():
            cols = st.columns([4, 1])
            with cols[0]:
                st.write(f"{element.value}")
            with cols[1]:
                if st.button("Удалить", key=f"del_{name}"):
                    del st.session_state['field_elements_simple'][name]
                    st.success(f"{name} был удалён.")
                    st.rerun()

    # Дополнительный раздел для работы с многочленами в простом поле
    if field_type == 'Простое поле':
        st.header("Работа с многочленами над GF(p)")

        st.subheader("Добавление многочлена")
        poly_input = st.text_input(
            "Введите коэффициенты многочлена (от старшей степени к свободному члену), через запятую:",
            key="poly_input"
        )
        poly_file = st.file_uploader("Или загрузите коэффициенты многочлена из файла:", type=["txt"], key="poly_file")

        if poly_file is not None:
            try:
                poly_input = poly_file.read().decode('utf-8')
            except Exception as e:
                st.error("Ошибка при чтении файла с коэффициентами многочлена.")

        if st.button("Добавить многочлен"):
            try:
                coeffs = [int(c.strip()) for c in poly_input.split(',')]  #
                poly = field.create_polynom(coeffs)

                poly_name = format_polynomial(poly.poly)

                st.session_state['polynomials_simple'][poly_name] = poly
                st.success(f"Добавлен {format_polynomial(poly.poly)}")
            except ValueError:
                st.error("Некорректный ввод коэффициентов многочлена.")
            except Exception as e:
                st.error("Ошибка при добавлении многочлена.")

        if st.session_state['polynomials_simple']:
            st.subheader("Список многочленов")
            for name, poly in st.session_state['polynomials_simple'].items():
                cols = st.columns([4, 1])
                with cols[0]:
                    st.write(f"{format_polynomial(poly.poly)}")
                with cols[1]:
                    if st.button("Удалить", key=f"del_poly_{name}"):
                        del st.session_state['polynomials_simple'][name]
                        st.success(f"{name} был удалён.")
                        st.rerun()

        st.header("Операции с многочленами над GF(p)")

        if st.session_state['polynomials_simple']:
            poly_names = list(st.session_state['polynomials_simple'].keys())
            if len(poly_names) < 2:
                st.info("Добавьте как минимум два многочлена для выполнения операций.")
            else:
                poly1_name = st.selectbox("Выберите первый многочлен", poly_names, key="poly1_op")
                poly2_name = st.selectbox("Выберите второй многочлен", poly_names, key="poly2_op")

                poly1 = st.session_state['polynomials_simple'][poly1_name]
                poly2 = st.session_state['polynomials_simple'][poly2_name]

                poly_operation = st.selectbox("Выберите операцию", ["Сложение", "Вычитание", "Умножение", "Деление"],
                                              key="poly_operation_select")

                if st.button("Выполнить операцию", key="compute_poly_operation"):
                    try:
                        if poly_operation == "Сложение":
                            result_poly = poly1 + poly2
                            operation_desc = "Сложение"

                        elif poly_operation == "Вычитание":
                            result_poly = poly1 - poly2
                            operation_desc = "Вычитание"

                        elif poly_operation == "Умножение":
                            result_poly = poly1 * poly2
                            operation_desc = "Умножение"

                        elif poly_operation == "Деление":
                            result_poly, remainder_poly = poly1 / poly2
                            operation_desc = "Деление"

                        if poly_operation != "Деление":
                            st.write(f"Результат: {format_polynomial(result_poly.poly)}")

                            entry = f"Операция: {operation_desc}\nМногочлен 1: {format_polynomial(poly1.poly)}\nМногочлен 2: {format_polynomial(poly2.poly)}\nРезультат: {format_polynomial(result_poly.poly)}\n"
                            log_operation(st.session_state['operation_log'], entry)

                            st.session_state['last_operation_result_polynomial'] = result_poly
                        else:
                            st.write(f"Частное: {format_polynomial(result_poly.poly)}")
                            st.write(f"Остаток: {format_polynomial(remainder_poly.poly)}")

                            entry = f"Операция: {operation_desc}\nМногочлен 1: {format_polynomial(poly1.poly)}\nМногочлен 2: {format_polynomial(poly2.poly)}\nЧастное: {format_polynomial(result_poly.poly)}\nОстаток: {format_polynomial(remainder_poly.poly)}\n"

                            log_operation(st.session_state['operation_log'], entry)
                            st.session_state['last_operation_result'] = None  # Остаток уже выведен
                    except ZeroDivisionError:
                        st.error("Деление на ноль.")
                    except Exception as e:
                        st.error(f"Ошибка при выполнении операции: {e}")

                if st.session_state.get('last_operation_result_polynomial') is not None:
                    if st.button("Сохранить результат как новый многочлен", key="save_result_poly"):
                        result = st.session_state['last_operation_result_polynomial']

                        poly_name = format_polynomial(result.poly)

                        st.session_state['polynomials_simple'][poly_name] = result
                        st.success(f"Результат сохранен как {poly_name}: {format_polynomial(result.poly)}")

                        st.session_state['last_operation_result_polynomial'] = None
                        st.rerun()

    st.header("Операции")

    element_names = list(st.session_state['field_elements_simple'].keys())

    if len(element_names) < 2 and field_type == 'Расширение поля':
        st.info("Добавьте как минимум два элемента для выполнения операций.")
    elif len(element_names) < 1 and field_type == 'Простое поле':
        st.info("Добавьте как минимум два элемента для выполнения операций.")
    else:
        if field_type == 'Расширение поля':
            el1_name = st.selectbox("Выберите первый элемент", element_names, key="el1_op")
            el2_name = st.selectbox("Выберите второй элемент", element_names, key="el2_op")
        else:
            el1_name = st.selectbox("Выберите первый элемент", element_names, key="el1_op")
            el2_name = st.selectbox("Выберите второй элемент", element_names, key="el2_op")

        el1 = st.session_state['field_elements_simple'][el1_name]
        el2 = st.session_state['field_elements_simple'][el2_name]

        operation = st.selectbox("Выберите операцию", ["Сложение", "Вычитание", "Умножение", "Деление"],
                                 key="operation_select")

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
                    st.session_state['last_operation_result_element'] = result
                    if field_type == 'Расширение поля':
                        st.write(f"Результат: {format_polynomial(result.poly)}")
                        entry = f"Операция: {operation}\nПоле: {field}\n{el1_name}: {format_polynomial(el1.poly)}\n{el2_name}: {format_polynomial(el2.poly)}\nРезультат: {format_polynomial(result.poly)}\n"
                    else:
                        st.write(f"Результат: {result.value}")
                        entry = f"Операция: {operation}\nПоле: {field}\n{el1_name}: {el1.value}\n{el2_name}: {el2.value}\nРезультат: {result.value}\n"

                    log_operation(st.session_state['operation_log'], entry)
            except ZeroDivisionError:
                st.error("Деление на ноль.")
            except Exception as e:
                st.error(f"Ошибка при вычислении: {e}")

        if st.session_state.get('last_operation_result_element') is not None:
            if st.button("Сохранить результат как новый элемент", key="save_result_element"):
                result = st.session_state['last_operation_result_element']

                if field_type == 'Расширение поля':
                    element_name = format_polynomial(result.poly)
                else:
                    element_name = result.value

                st.session_state['field_elements_simple'][element_name] = result

                st.success(f"Результат сохранен как {element_name}")
                st.session_state['last_operation_result_element'] = None
                st.rerun()

    st.header("Обратные элементы")

    if field_type == 'Расширение поля':
        st.subheader("Найти обратный элемент")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для нахождения обратных.")
        else:
            el_inv_name = st.selectbox("Выберите элемент для нахождения обратного", element_names, key="el_inv_select")

            el_inv = st.session_state['field_elements_simple'][el_inv_name]

            if st.button("Найти обратный"):
                try:
                    inverse_el = el_inv.inverse()
                    st.session_state['last_inverse_result_polynomial'] = inverse_el
                    st.write(f"Обратный элемент для {el_inv_name}: {format_polynomial(inverse_el.poly)}")
                    entry = f"Операция: Нахождение обратного элемента\nПоле: {field}\nЭлемент: {format_polynomial(el_inv.poly)}\nОбратный элемент: {format_polynomial(inverse_el.poly)}\n"
                    log_operation(st.session_state['operation_log'], entry)
                except Exception as e:
                    st.error("Этот элемент не имеет обратного.")

            if st.session_state.get('last_inverse_result_polynomial') is not None:
                if st.button("Сохранить обратный элемент как новый многочлен", key="save_inverse_element_poly"):
                    inverse_el = st.session_state['last_inverse_result_polynomial']

                    element_name = format_polynomial(inverse_el.poly)

                    st.session_state['field_elements_simple'][element_name] = inverse_el
                    st.success(f"Обратный элемент сохранен как {element_name}")

                    st.session_state['last_inverse_result_polynomial'] = None
                    st.rerun()

    elif field_type == 'Простое поле':
        st.subheader("Найти обратный элемент")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для нахождения обратных.")
        else:
            el_inv_name = st.selectbox("Выберите элемент для нахождения обратного", element_names,
                                       key="el_inv_select_simple")

            el_inv = st.session_state['field_elements_simple'][el_inv_name]

            if st.button("Найти обратный"):
                try:
                    inverse_el = el_inv.inverse()

                    st.session_state['last_inverse_result_element'] = inverse_el
                    st.write(f"Обратный элемент для {el_inv_name}: {inverse_el.value}")

                    entry = f"Операция: Нахождение обратного элемента\nПоле: {field}\nЭлемент: {el_inv.value}\nОбратный элемент: {inverse_el.value}\n"

                    log_operation(st.session_state['operation_log'], entry)
                except Exception as e:
                    st.error("Этот элемент не имеет обратного.")

            if st.session_state.get('last_inverse_result_element') is not None:
                if st.button("Сохранить обратный элемент как новый элемент", key="save_inverse_element"):
                    inverse_el = st.session_state['last_inverse_result_element']
                    element_name = inverse_el.value

                    st.session_state['field_elements_simple'][element_name] = inverse_el
                    st.success(f"Обратный элемент сохранен как {element_name}: {inverse_el.value}")

                    st.session_state['last_inverse_result_element'] = None
                    st.rerun()

    if field_type == 'Расширение поля':
        st.header("Вычисление значений многочленов")
        st.subheader("Вычислить значение многочлена")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для выполнения вычислений.")
        else:
            el_eval_name = st.selectbox("Выберите элемент для вычисления", element_names, key="el_eval_select")
            el_eval = st.session_state['field_elements_simple'][el_eval_name]
            x_value_input = st.text_input(
                "Введите значение для подстановки (коэффициенты многочлена через запятую):",
                key="x_value_input"
            )
            x_value_file = st.file_uploader("Или загрузите значение для подстановки из файла:", type=["txt"],
                                            key="x_value_file")

            if x_value_file is not None:
                try:
                    x_value_input = x_value_file.read().decode('utf-8')
                except Exception as e:
                    st.error("Ошибка при чтении файла со значением для подстановки.")

            if st.button("Вычислить значение"):
                try:
                    x_coeffs = [int(c.strip()) % p for c in x_value_input.split(',')]
                    if len(x_coeffs) > len(field.modulus_polynomial.coeffs) - 1:
                        st.warning(
                            f"Максимальная степень элемента поля: {len(field.modulus_polynomial.coeffs) - 2}. Привожу многочлен по модулю.")
                    x_element = field.create_element(x_coeffs)
                    result = el_eval.calculate_value(x_element)

                    st.session_state['last_evaluation_result'] = result
                    st.write(
                        f"Значение {format_polynomial(el_eval.poly)} при {format_polynomial(x_element.poly)}: {format_polynomial(result.poly)}")

                    entry = f"Операция: Вычисление значения многочлена\nПоле: {field}\nМногочлен: {format_polynomial(el_eval.poly)}\nЗначение: {format_polynomial(x_element.poly)}\nРезультат: {format_polynomial(result.poly)}\n"
                    log_operation(st.session_state['operation_log'], entry)
                except Exception as e:
                    st.error("Некорректный ввод значения для вычисления.")

    # Дополнительный раздел для работы с многочленами в простом поле
    if field_type == 'Простое поле' and st.session_state['polynomials_simple']:
        st.header("Вычисление значений многочленов над GF(p)")

        poly_names = list(st.session_state['polynomials_simple'].keys())
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not poly_names:
            st.info("Добавьте многочлены для выполнения вычислений.")
        elif not element_names:
            st.info("Добавьте элементы поля для выполнения вычислений.")
        else:
            selected_poly_name = st.selectbox("Выберите многочлен", poly_names, key="selected_poly")
            selected_poly = st.session_state['polynomials_simple'][selected_poly_name]
            selected_element_name = st.selectbox("Выберите элемент для подстановки", element_names,
                                                 key="selected_element")
            selected_element = st.session_state['field_elements_simple'][selected_element_name]

            if st.button("Вычислить значение"):
                try:
                    result = selected_poly.calculate_value(selected_element)

                    st.write(
                        f"При x = {selected_element.value}, значение {format_polynomial(selected_poly.poly)} = {result.value}")
                    entry = f"Операция: Вычисление значения многочлена над GF({p})\nМногочлен: {format_polynomial(selected_poly.poly)}\nЭлемент для подстановки: {selected_element.value}\nРезультат: {result.value}\n"

                    log_operation(st.session_state['operation_log'], entry)
                except Exception as e:
                    st.error("Ошибка при вычислении значения многочлена.")

else:
    st.info("Пожалуйста, определите поле для продолжения.")

if st.session_state['operation_log']:
    operation_log_str = "\n".join(st.session_state['operation_log'])
    st.download_button("Скачать лог операций", operation_log_str, file_name="operation_log.txt")
