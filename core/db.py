import sqlite3


def initialize_database(db_path='irreducible_polynomials.db'):
    """
    Создает базу данных и таблицу, если они не существуют.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS irreducible_polynomials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            p INTEGER NOT NULL,
            n INTEGER NOT NULL,
            coefficients TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(p, n, coefficients)
        )
    ''')
    conn.commit()
    conn.close()


def save_polynomials_to_db(polynomials, p, n, time, db_path='irreducible_polynomials.db'):
    """
    Сохраняет список многочленов в базу данных.
    """
    if not polynomials:
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.executemany('''
            INSERT OR IGNORE INTO irreducible_polynomials (p, n, coefficients, timestamp)
            VALUES (?, ?, ?, ?)
        ''', [(p, n, ", ".join(map(str, poly)), time.strftime('%Y-%m-%d %H:%M:%S')) for poly in polynomials])
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении многочленов в базу данных: {e}")
    finally:
        conn.close()


def get_saved_polynomials(p=None, n=None, db_path='irreducible_polynomials.db'):
    """
    Извлекает сохраненные многочлены из базы данных с фильтрацией по p и n.
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT p, n, coefficients, timestamp  FROM irreducible_polynomials WHERE 1=1"
    params = []
    if p is not None:
        query += " AND p = ?"
        params.append(p)
    if n is not None:
        query += " AND n = ?"
        params.append(n)
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results
