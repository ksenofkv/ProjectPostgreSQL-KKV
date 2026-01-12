from dbtable import DbTable
from tables.drugs import DrugsTable


class PharmaciesTable(DbTable):
    """
    Класс для работы с таблицей аптек в базе данных.
    Таблица содержит информацию об адресе, телефоне и ближайшей станции метро.
    """

    def table_name(self):
        """Возвращает имя таблицы с префиксом (например, 'myapp_pharmacies')."""
        return self.dbconn.prefix + "pharmacies"

    def columns(self):
        """
        Определяет структуру колонок таблицы.
        Все поля обязательны (NOT NULL), id — автоинкрементный первичный ключ.
        """
        return {
            "id": ["serial", "NOT NULL", "PRIMARY KEY"],
            "address": ["varchar(500)", "NOT NULL"],                 # Адрес аптеки
            "phone_number": ["varchar(20)", "NOT NULL"],             # Телефон
            "nearest_metro_station": ["varchar(255)", "NOT NULL"],   # Ближайшее метро
        }

    def primary_key(self):
        """Возвращает список колонок первичного ключа."""
        return ['id']

    def table_constraints(self):
        """
        Дополнительные ограничения уровня таблицы.
        Раскомментируйте строку ниже, если адрес должен быть уникальным.
        """
        # return ["UNIQUE(address)"]
        return []

    # ─────────────── Методы поиска ───────────────

    def find_by_address(self, address):
        """
        Находит аптеку по точному совпадению адреса.
        :param address: строка — адрес аптеки
        :return: кортеж с данными (id, address, phone_number, nearest_metro_station) или None
        """
        sql = f"SELECT * FROM {self.table_name()} WHERE address = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (address,))
            return cur.fetchone()

    # ─────────────── Методы удаления ───────────────

    def delete_by_address(self, address):
        """
        Удаляет все аптеки с указанным адресом.
        ⚠️ Если адрес не уникален — удалятся все совпадения!
        :param address: адрес для удаления
        :return: количество удалённых строк
        """
        sql = f"DELETE FROM {self.table_name()} WHERE address = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (address,))
            self.dbconn.conn.commit()
            return cur.rowcount

    def delete_with_drugs(self, pharmacy_id):
        """
        Удаляет аптеку и все её лекарства (каскадно).
        :param pharmacy_id: ID аптеки
        :return: количество удалённых строк (0 или 1)
        """
        sql = f"DELETE FROM {self.table_name()} WHERE id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (pharmacy_id,))
            self.dbconn.conn.commit()
            return cur.rowcount

    # ─────────────── Методы обновления ───────────────

    def update_by_address(self, old_address, new_address, phone_number, nearest_metro_station):
        """
        Обновляет данные аптеки по старому адресу.
        ⚠️ Риск: если несколько аптек имеют old_address — обновятся все!
        
        :param old_address: текущий адрес (условие WHERE)
        :param new_address: новый адрес
        :param phone_number: новый телефон
        :param nearest_metro_station: новая станция метро
        :return: количество обновлённых строк
        """
        sql = f"""
            UPDATE {self.table_name()}
            SET address = %s, phone_number = %s, nearest_metro_station = %s
            WHERE address = %s
        """
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (new_address, phone_number, nearest_metro_station, old_address))
            self.dbconn.conn.commit()
            return cur.rowcount

    def update_by_id(self, pharmacy_id, address, phone_number, nearest_metro_station):
        """
        Безопасное обновление аптеки по уникальному идентификатору.
        Гарантирует изменение ровно одной записи (если id существует).
        
        :param pharmacy_id: id аптеки
        :param address: новый адрес
        :param phone_number: новый телефон
        :param nearest_metro_station: новая станция метро
        :return: количество обновлённых строк (0 или 1)
        """
        sql = f"""
            UPDATE {self.table_name()}
            SET address = %s, phone_number = %s, nearest_metro_station = %s
            WHERE id = %s
        """
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (address, phone_number, nearest_metro_station, pharmacy_id))
            self.dbconn.conn.commit()
            return cur.rowcount

    # ─────────────── Метод вставки ───────────────

    def insert_one(self, vals):
        """
        Вставляет новую аптеку.
        :param vals: список [address, phone_number, nearest_metro_station]
        :return: id вставленной записи
        """
        cols = self.column_names_without_id()  # ['address', 'phone_number', 'nearest_metro_station']
        if len(vals) != len(cols):
            raise ValueError(f"Ожидалось {len(cols)} значений, получено {len(vals)}")

        placeholders = ", ".join(["%s"] * len(vals))
        col_list = ", ".join(cols)
        sql = f"INSERT INTO {self.table_name()} ({col_list}) VALUES ({placeholders}) RETURNING id"
        
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, vals)
            self.dbconn.conn.commit()
            return cur.fetchone()[0]  # Возвращаем сгенерированный id

    # ─────────────── Метод получения лекарств ───────────────

    def get_drugs(self, pharmacy_id):
        """
        Получить все лекарства в указанной аптеке.
        :param pharmacy_id: ID аптеки
        :return: список кортежей с лекарствами
        """
        sql = f"SELECT * FROM {DrugsTable().table_name()} WHERE pharmacy_id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (pharmacy_id,))
            return cur.fetchall()