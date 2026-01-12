# Базовые действия с таблицами

from dbconnection import *

class DbTable:
    # Глобальное соединение с БД (должно быть инициализировано до использования класса)
    dbconn = None

    def __init__(self):
        # Проверяем, что соединение с БД установлено
        if DbTable.dbconn is None:
            raise RuntimeError("DbTable.dbconn не инициализирован! "
                               "Убедитесь, что вы присвоили DbTable.dbconn = ваше_соединение.")

    def table_name(self):
        """Возвращает имя таблицы с префиксом."""
        return self.dbconn.prefix + "table"

    def columns(self):
        """
        Определяет структуру таблицы.
        Формат: {"имя_колонки": ["тип", "ограничение1", "ограничение2", ...]}
        """
        # ⚠️ ВАЖНО: ранее здесь был PRIMARY KEY на 'test', но primary_key() возвращал 'id'
        # Это противоречие! Исправлено: теперь используется 'id' как PK.
        return {
            "id": ["serial", "PRIMARY KEY"]
        }

    def column_names(self):
        """Возвращает отсортированный список имён всех колонок."""
        return sorted(self.columns().keys())

    def primary_key(self):
        """
        Возвращает список колонок, составляющих первичный ключ.
        По умолчанию — ['id'].
        """
        # 🔁 Альтернатива: можно динамически определять PK из columns(),
        # но для простоты оставим явное указание.
        return ['id']

    def column_names_without_id(self):
        """Возвращает список колонок без 'id' (обычно для INSERT)."""
        res = self.column_names()
        if 'id' in res:
            res.remove('id')
        return res

    def table_constraints(self):
        """
        Дополнительные ограничения уровня таблицы (например, FOREIGN KEY, CHECK).
        Возвращает список строк SQL-ограничений.
        """
        return []

    def create(self):
        """Создаёт таблицу в БД."""
        # Формируем определения колонок
        arr = [
            k + " " + " ".join(v)
            for k, v in sorted(self.columns().items())
        ]
        sql = "CREATE TABLE " + self.table_name() + "("
        sql += ", ".join(arr + self.table_constraints())
        sql += ")"

        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            self.dbconn.conn.commit()
        finally:
            cur.close()

    def drop(self):
        """Удаляет таблицу, если она существует."""
        sql = "DROP TABLE IF EXISTS " + self.table_name()
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            self.dbconn.conn.commit()
        finally:
            cur.close()

    def insert_one(self, vals):
        """
        Вставляет одну запись в таблицу.
        :param vals: список значений (без id, если id — serial/PK)
        """
        cols = self.column_names_without_id()
        if len(vals) != len(cols):
            raise ValueError(
                f"Ожидалось {len(cols)} значений для колонок {cols}, "
                f"получено {len(vals)}: {vals}"
            )

        # ✅ ИСПОЛЬЗУЕМ ПАРАМЕТРИЗОВАННЫЙ ЗАПРОС — ЗАЩИТА ОТ SQL-ИНЪЕКЦИЙ!
        placeholders = ", ".join(["%s"] * len(vals))
        col_list = ", ".join(cols)
        sql = f"INSERT INTO {self.table_name()} ({col_list}) VALUES ({placeholders})"

        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, vals)  # ← значения передаются отдельно, безопасно
            self.dbconn.conn.commit()
        finally:
            cur.close()

    def first(self):
        """Возвращает первую запись (по PK) или None, если таблица пуста."""
        sql = "SELECT * FROM " + self.table_name()
        sql += " ORDER BY " + ", ".join(self.primary_key())
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchone()
        finally:
            cur.close()

    def last(self):
        """Возвращает последнюю запись (по PK) или None, если таблица пуста."""
        sql = "SELECT * FROM " + self.table_name()
        sql += " ORDER BY " + ", ".join([x + " DESC" for x in self.primary_key()])
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchone()
        finally:
            cur.close()

    def all(self):
        """Возвращает все записи, отсортированные по PK."""
        sql = "SELECT * FROM " + self.table_name()
        sql += " ORDER BY " + ", ".join(self.primary_key())
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()