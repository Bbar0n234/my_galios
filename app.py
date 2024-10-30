import streamlit as st
import numpy as np

from sympy import isprime

from core import (
    GaloisFieldExtension,
    GaloisFieldSimple,
    find_irreducible_polynomials_batch,
    format_polynomial
)

import streamlit.components.v1 as components

def create_copy_button(text, button_id):
    # HTML и JavaScript для кнопки копирования с подсветкой при нажатии
    copy_button_html = f"""
    <style>
    .copy-button {{
        background-color: #4CAF50; /* Зеленый */
        border: none;
        color: white;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        transition: background-color 0.3s;
    }}
    .copy-button.copied {{
        background-color: #555555; /* Темно-серый при копировании */
    }}
    </style>
    <button class="copy-button" onclick="copyToClipboard('poly_{button_id}', this)">Скопировать</button>
    <input type="hidden" value="{text}" id="poly_{button_id}">
    <script>
    function copyToClipboard(elementId, btn) {{
        var copyText = document.getElementById(elementId).value;
        navigator.clipboard.writeText(copyText).then(function() {{
            /* Копирование успешно */
            btn.classList.add('copied');
            setTimeout(function() {{
                btn.classList.remove('copied');
            }}, 500); 
        }}, function(err) {{
            /* Копирование не удалось */
            // Можно добавить обработку ошибок, если необходимо
        }});
    }}
    </script>
    """
    components.html(copy_button_html, height=60, scrolling=False)

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

if 'irreducible_pols' not in st.session_state:
    st.session_state['irreducible_pols'] = []
if 'offset' not in st.session_state:
    st.session_state['offset'] = 0
if 'batch_size' not in st.session_state:
    st.session_state['batch_size'] = 50
if 'p_irreducible' not in st.session_state:
    st.session_state['p_irreducible'] = None
if 'n_irreducible' not in st.session_state:
    st.session_state['n_irreducible'] = None

st.title("Калькулятор поля Галуа GF(p^n)")

field_type = st.radio("Выберите тип поля", ('Расширение поля', 'Простое поле', 'Поиск неприводимых многочленов'))
st.session_state['field_type'] = field_type

if field_type != 'Поиск неприводимых многочленов':
    st.header("Определение поля")

if field_type in ["Расширение поля", "Простое поле"]:

    p = st.number_input("Введите характеристику p (простое число):", min_value=2, value=2, step=1)

    if not isprime(p):
        st.error(f"{p} не является простым числом! Пожалуйста, введите простое число.")
        # Логирование ошибки: некорректное значение p
        entry = f"Ошибка: Некорректная характеристика поля p={p} (непростое число)."
        log_operation(st.session_state['operation_log'], entry)
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
            # Логирование исключения при чтении файла
            entry = f"Ошибка при чтении файла с коэффициентами неприводимого многочлена: {str(e)}. Содержимое файла: {modulus_file.name}"
            log_operation(st.session_state['operation_log'], entry)

    # Парсинг коэффициентов
    try:
        modulus_coeffs = [int(c.strip()) % p for c in coeffs_input.split(',')] if p else None
    except ValueError as e:
        modulus_coeffs = None
        st.error("Некорректный ввод коэффициентов многочлена.")
        # Логирование исключения при парсинге коэффициентов
        entry = f"Ошибка при парсинге коэффициентов многочлена: {str(e)}. Введённые коэффициенты: '{coeffs_input}'"
        log_operation(st.session_state['operation_log'], entry)

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
            # Логирование ошибки: недостаточная степень многочлена
            entry = f"Ошибка: Многочлен степени {len(modulus_coeffs)-1} недостаточно высок для расширения поля GF({p}^n). Коэффициенты: {modulus_coeffs}"
            log_operation(st.session_state['operation_log'], entry)
        else:
            try:
                field = GaloisFieldExtension(p, modulus_coeffs)
                st.success(f"Поле {field} успешно создано.")

                st.write("**Многочлен, задающий поле:**")
                st.write(format_polynomial(field.modulus_polynomial))
            except ValueError as e:
                st.error(str(e))
                # Логирование исключения при создании поля
                entry = f"Ошибка при создании расширения поля GF({p}^n) с коэффициентами {modulus_coeffs}: {str(e)}"
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error("Ошибка при создании поля.")
                # Логирование общего исключения при создании поля
                entry = f"Неизвестная ошибка при создании расширения поля GF({p}^n) с коэффициентами {modulus_coeffs}: {str(e)}"
                log_operation(st.session_state['operation_log'], entry)
    else:
        if modulus_coeffs is None and p:
            st.error("Пожалуйста, введите корректные целые числа для коэффициентов неприводимого многочлена.")
            # Логирование ошибки: некорректные коэффициенты
            entry = f"Ошибка: Некорректные коэффициенты неприводимого многочлена. Введённые коэффициенты: '{coeffs_input}'"
            log_operation(st.session_state['operation_log'], entry)
        elif p is None:
            st.info("Пожалуйста, введите корректную характеристику поля p.")
            # Логирование информации о необходимости ввода p
            entry = "Информация: Требуется корректная характеристика поля p для продолжения."
            log_operation(st.session_state['operation_log'], entry)

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
        try:
            field = GaloisFieldSimple(p)
            st.success(f"Поле {field} успешно создано.")
        except Exception as e:
            st.error("Ошибка при создании простого поля.")
            # Логирование исключения при создании простого поля
            entry = f"Ошибка при создании простого поля GF({p}): {str(e)}"
            log_operation(st.session_state['operation_log'], entry)
    else:
        st.info("Пожалуйста, введите корректную характеристику поля p.")
        # Логирование информации о необходимости ввода p
        entry = "Информация: Требуется корректная характеристика поля p для продолжения."
        log_operation(st.session_state['operation_log'], entry)

elif field_type == 'Поиск неприводимых многочленов':
    st.header("Поиск неприводимых многочленов")

    p_irreducible = st.number_input("Введите характеристику p (простое число):", min_value=2, value=2, step=1, key='p_irreducible_input')
    n_irreducible = st.number_input("Введите степень многочлена n:", min_value=1, value=3, step=1, key='n_irreducible_input')

    # Check if p is prime
    if not isprime(p_irreducible):
        st.error(f"{p_irreducible} не является простым числом! Пожалуйста, введите простое число.")
        p_irreducible = None

    if st.button("Поиск неприводимых многочленов"):
        if p_irreducible is None:
            st.error("Введите корректное простое число p.")
        else:
            # Initialize the variables
            st.session_state['p_irreducible'] = int(p_irreducible)
            st.session_state['n_irreducible'] = int(n_irreducible)
            st.session_state['offset'] = 0
            st.session_state['irreducible_pols'] = []
            st.session_state['batch_size'] = 100

            # Get the first batch of polynomials
            with st.spinner("Поиск неприводимых многочленов..."):
                irreducible_polys = find_irreducible_polynomials_batch(
                    st.session_state['p_irreducible'],
                    st.session_state['n_irreducible'],
                    st.session_state['batch_size'],
                    st.session_state['offset']
                )
                st.session_state['irreducible_pols'].extend(irreducible_polys)
                st.session_state['offset'] += st.session_state['batch_size']

    # Check if p or n has changed to reset the state
    if (st.session_state.get('p_irreducible') != p_irreducible or
        st.session_state.get('n_irreducible') != n_irreducible):
        if p_irreducible is not None:
            st.session_state['p_irreducible'] = int(p_irreducible)
        else:
            st.session_state['p_irreducible'] = None
        st.session_state['n_irreducible'] = int(n_irreducible)
        st.session_state['offset'] = 0
        st.session_state['irreducible_pols'] = []

    # Display the polynomials found so far
    if st.session_state['irreducible_pols']:
        st.write(f"Найдено {len(st.session_state['irreducible_pols'])} неприводимых многочленов:")
        for idx, poly_coeffs in enumerate(st.session_state['irreducible_pols']):
            curr_irr_p = st.session_state['p_irreducible']

            poly_coeffs = [coef % curr_irr_p for coef in poly_coeffs]
            degree = len(poly_coeffs) - 1

            poly = np.poly1d(poly_coeffs)
            st.write(f"{format_polynomial(poly)}")
            create_copy_button(", ".join(map(str, poly_coeffs)), f"{idx}_{curr_irr_p}_{degree}")

        # Button to get more polynomials
        if st.button("Ещё"):
            with st.spinner("Поиск неприводимых многочленов..."):
                irreducible_polys = find_irreducible_polynomials_batch(
                    st.session_state['p_irreducible'],
                    st.session_state['n_irreducible'],
                    st.session_state['batch_size'],
                    st.session_state['offset']
                )
                if irreducible_polys:
                    st.session_state['irreducible_pols'].extend(irreducible_polys)
                    st.session_state['offset'] += st.session_state['batch_size']
                else:
                    st.write("Больше неприводимых многочленов не найдено.")

                st.rerun()


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
                # Логирование исключения при чтении файла элемента
                entry = f"Ошибка при чтении файла с коэффициентами элемента: {str(e)}. Содержимое файла: {new_poly_file.name}"
                log_operation(st.session_state['operation_log'], entry)

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
                # Логирование исключения при добавлении элемента
                entry = f"Ошибка при добавлении элемента поля GF({p}^n): {str(e)}. Введённые коэффициенты: '{new_poly_input}'"
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error("Некорректный ввод коэффициентов многочлена.")
                # Логирование общего исключения при добавлении элемента
                entry = f"Ошибка при добавлении элемента поля GF({p}^n): {str(e)}. Введённые коэффициенты: '{new_poly_input}'"
                log_operation(st.session_state['operation_log'], entry)
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
                # Логирование исключения при добавлении элемента
                entry = f"Ошибка при добавлении элемента поля GF({p}): {str(e)}. Введённое значение: {new_element_value}"
                log_operation(st.session_state['operation_log'], entry)

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
                    # Логирование удаления элемента
                    entry = f"Удаление элемента поля GF({p}^n): {name}"
                    log_operation(st.session_state['operation_log'], entry)
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
                    # Логирование удаления элемента
                    entry = f"Удаление элемента поля GF({p}): {name}"
                    log_operation(st.session_state['operation_log'], entry)
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
                # Логирование исключения при чтении файла многочлена
                entry = f"Ошибка при чтении файла с коэффициентами многочлена: {str(e)}. Содержимое файла: {poly_file.name}"
                log_operation(st.session_state['operation_log'], entry)

        if st.button("Добавить многочлен"):
            try:
                coeffs = [int(c.strip()) for c in poly_input.split(',')]  #
                poly = field.create_polynom(coeffs)

                poly_name = format_polynomial(poly.poly)

                st.session_state['polynomials_simple'][poly_name] = poly
                st.success(f"Добавлен {format_polynomial(poly.poly)}")
            except ValueError as e:
                st.error("Некорректный ввод коэффициентов многочлена.")
                # Логирование исключения при добавлении многочлена
                entry = f"Ошибка при добавлении многочлена над GF({p}): {str(e)}. Введённые коэффициенты: '{poly_input}'"
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error("Ошибка при добавлении многочлена.")
                # Логирование общего исключения при добавлении многочлена
                entry = f"Ошибка при добавлении многочлена над GF({p}): {str(e)}. Введённые коэффициенты: '{poly_input}'"
                log_operation(st.session_state['operation_log'], entry)

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
                        # Логирование удаления многочлена
                        entry = f"Удаление многочлена над GF({p}): {name}"
                        log_operation(st.session_state['operation_log'], entry)
                        st.rerun()

        st.header("Операции с многочленами над GF(p)")

        if st.session_state['polynomials_simple']:
            poly_names = list(st.session_state['polynomials_simple'].keys())
            if len(poly_names) < 2:
                st.info("Добавьте как минимум два многочлена для выполнения операций.")
                # Логирование информации о недостатке многочленов для операций
                entry = "Информация: Недостаточно многочленов для выполнения операций. Требуется минимум два."
                log_operation(st.session_state['operation_log'], entry)
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
                        # Логирование деления на ноль
                        entry = f"Ошибка: Деление многочленов. Делитель: {format_polynomial(poly2.poly)} (деление на ноль)."
                        log_operation(st.session_state['operation_log'], entry)
                    except Exception as e:
                        st.error(f"Ошибка при выполнении операции: {e}")
                        # Логирование общего исключения при выполнении операции
                        entry = f"Ошибка при выполнении операции '{poly_operation}' над многочленами {format_polynomial(poly1.poly)} и {format_polynomial(poly2.poly)}: {str(e)}"
                        log_operation(st.session_state['operation_log'], entry)

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
        # Логирование информации о недостатке элементов для операций
        entry = "Информация: Недостаточно элементов для выполнения операций. Требуется минимум два."
        log_operation(st.session_state['operation_log'], entry)
    elif len(element_names) < 1 and field_type == 'Простое поле':
        st.info("Добавьте как минимум два элемента для выполнения операций.")
        # Логирование информации о недостатке элементов для операций
        entry = "Информация: Недостаточно элементов для выполнения операций. Требуется минимум один."
        log_operation(st.session_state['operation_log'], entry)
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
                # Логирование деления на ноль
                entry = f"Ошибка: Деление элемента {el1_name} на элемент {el2_name} (деление на ноль)."
                log_operation(st.session_state['operation_log'], entry)
            except Exception as e:
                st.error(f"Ошибка при вычислении: {e}")
                # Логирование общего исключения при вычислении операции
                entry = f"Ошибка при выполнении операции '{operation}' над элементами {el1_name} и {el2_name}: {str(e)}"
                log_operation(st.session_state['operation_log'], entry)

        if st.session_state.get('last_operation_result_element') is not None:
            if st.button("Сохранить результат как новый элемент", key="save_result_element"):
                result = st.session_state['last_operation_result_element']

                if field_type == 'Расширение поля':
                    element_name = format_polynomial(result.poly)
                else:
                    element_name = result.value

                st.session_state['field_elements_simple'][element_name] = result

                st.success(f"Результат сохранен как {element_name}")
                # Логирование сохранения результата операции
                entry = f"Сохранение результата операции как нового элемента: {element_name}"
                log_operation(st.session_state['operation_log'], entry)

                st.session_state['last_operation_result_element'] = None
                st.rerun()

    st.header("Обратные элементы")

    if field_type == 'Расширение поля':
        st.subheader("Найти обратный элемент")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для нахождения обратных.")
            # Логирование информации о необходимости добавления элементов для нахождения обратных
            entry = "Информация: Нет элементов поля для нахождения обратных элементов."
            log_operation(st.session_state['operation_log'], entry)
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
                    # Логирование отсутствия обратного элемента
                    entry = f"Ошибка: Невозможно найти обратный элемент для {format_polynomial(el_inv.poly)} в поле {field}. Причина: {str(e)}"
                    log_operation(st.session_state['operation_log'], entry)

            if st.session_state.get('last_inverse_result_polynomial') is not None:
                if st.button("Сохранить обратный элемент как новый многочлен", key="save_inverse_element_poly"):
                    inverse_el = st.session_state['last_inverse_result_polynomial']

                    element_name = format_polynomial(inverse_el.poly)

                    st.session_state['field_elements_simple'][element_name] = inverse_el
                    st.success(f"Обратный элемент сохранен как {element_name}")

                    # Логирование сохранения обратного элемента
                    entry = f"Сохранение обратного элемента как нового элемента: {element_name}"
                    log_operation(st.session_state['operation_log'], entry)

                    st.session_state['last_inverse_result_polynomial'] = None
                    st.rerun()

    elif field_type == 'Простое поле':
        st.subheader("Найти обратный элемент")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для нахождения обратных.")
            # Логирование информации о необходимости добавления элементов для нахождения обратных
            entry = "Информация: Нет элементов поля для нахождения обратных элементов."
            log_operation(st.session_state['operation_log'], entry)
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
                    # Логирование отсутствия обратного элемента
                    entry = f"Ошибка: Невозможно найти обратный элемент для {el_inv.value} в поле {field}. Причина: {str(e)}"
                    log_operation(st.session_state['operation_log'], entry)

            if st.session_state.get('last_inverse_result_element') is not None:
                if st.button("Сохранить обратный элемент как новый элемент", key="save_inverse_element"):
                    inverse_el = st.session_state['last_inverse_result_element']
                    element_name = inverse_el.value

                    st.session_state['field_elements_simple'][element_name] = inverse_el

                    st.success(f"Обратный элемент сохранен как {element_name}: {inverse_el.value}")

                    # Логирование сохранения обратного элемента
                    entry = f"Сохранение обратного элемента как нового элемента: {element_name}"
                    log_operation(st.session_state['operation_log'], entry)

                    st.session_state['last_inverse_result_element'] = None
                    st.rerun()
        

    if field_type == 'Расширение поля':
        st.header("Вычисление значений многочленов")
        st.subheader("Вычислить значение многочлена")
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not element_names:
            st.info("Добавьте элементы поля для выполнения вычислений.")
            # Логирование информации о необходимости добавления элементов для вычислений
            entry = "Информация: Нет элементов поля для выполнения вычислений."
            log_operation(st.session_state['operation_log'], entry)
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
                    # Логирование исключения при чтении файла значения для подстановки
                    entry = f"Ошибка при чтении файла со значением для подстановки: {str(e)}. Содержимое файла: {x_value_file.name}"
                    log_operation(st.session_state['operation_log'], entry)

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
                    # Логирование исключения при вычислении значения многочлена
                    entry = f"Ошибка при вычислении значения многочлена: {str(e)}. Многочлен: {format_polynomial(el_eval.poly)}, Значение для подстановки: '{x_value_input}'"
                    log_operation(st.session_state['operation_log'], entry)

    # Дополнительный раздел для работы с многочленами в простом поле
    if field_type == 'Простое поле' and st.session_state['polynomials_simple']:
        st.header("Вычисление значений многочленов над GF(p)")

        poly_names = list(st.session_state['polynomials_simple'].keys())
        element_names = list(st.session_state['field_elements_simple'].keys())
        if not poly_names:
            st.info("Добавьте многочлены для выполнения вычислений.")
            # Логирование информации о необходимости добавления многочленов
            entry = "Информация: Нет многочленов для выполнения вычислений."
            log_operation(st.session_state['operation_log'], entry)
        elif not element_names:
            st.info("Добавьте элементы поля для выполнения вычислений.")
            # Логирование информации о необходимости добавления элементов
            entry = "Информация: Нет элементов поля для выполнения вычислений."
            log_operation(st.session_state['operation_log'], entry)
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
                    # Логирование исключения при вычислении значения многочлена
                    entry = f"Ошибка при вычислении значения многочлена: {str(e)}. Многочлен: {format_polynomial(selected_poly.poly)}, Элемент для подстановки: {selected_element.value}"
                    log_operation(st.session_state['operation_log'], entry)

elif field_type != "Поиск неприводимых многочленов":
    st.info("Пожалуйста, определите поле для продолжения.")
    entry = "Информация: Необходимо определить поле Галуа для продолжения работы."
    log_operation(st.session_state['operation_log'], entry)

if st.session_state['operation_log']:
    operation_log_str = "\n".join(st.session_state['operation_log'])
    st.download_button("Скачать лог операций", operation_log_str, file_name="operation_log.txt")
