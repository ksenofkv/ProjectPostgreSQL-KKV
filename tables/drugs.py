from dbtable import DbTable


class DrugsTable(DbTable):
    """
    Класс для работы с таблицей лекарств в базе данных.
    Содержит информацию о названии, дозировке, производителе, цене
    и привязке к аптеке (pharmacy_id).
    """
    def find_by_category(self, category_id):
        sql = f"SELECT * FROM {self.table_name()} WHERE category_id = %s ORDER BY drug_name"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (category_id,))
            return cur.fetchall()

    def table_name(self):
        """Возвращает имя таблицы с префиксом (например, 'myapp_drugs')."""
        return self.dbconn.prefix + "drugs"

    def columns(self):
        """Определяет структуру таблицы лекарств."""
        return {
            "drug_id": ["serial", "PRIMARY KEY"],
            "drug_name": ["varchar(255)", "NOT NULL"],
            "dosage": ["varchar(100)"],
            "quantity_or_volume": ["varchar(100)"],
            "manufacturer": ["varchar(255)"],
            "instructions": ["text"],
            "requires_prescription": ["boolean", "NOT NULL", "DEFAULT FALSE"],
            "price": ["numeric(10,2)", "NOT NULL"],
            "pharmacy_id": ["integer", "REFERENCES pharmacies(id) ON DELETE CASCADE"]
        }

    def primary_key(self):
        """Первичный ключ таблицы drugs — это drug_id."""
        return ['drug_id']

    def table_constraints(self):
        """Ограничения уровня таблицы."""
        return [
            "CHECK (price >= 0)"
        ]

    # ─────────────── Методы поиска ───────────────

    def find_by_id(self, drug_id):
        """
        Находит лекарство по уникальному идентификатору.
        :param drug_id: ID лекарства
        :return: кортеж с данными или None, если не найдено
        """
        sql = f"SELECT * FROM {self.table_name()} WHERE drug_id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (drug_id,))
            return cur.fetchone()

    def find_by_name(self, drug_name):
        """
        Находит все лекарства с точным совпадением названия.
        :param drug_name: название лекарства
        :return: список кортежей
        """
        sql = f"SELECT * FROM {self.table_name()} WHERE drug_name = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (drug_name,))
            return cur.fetchall()

    def find_by_pharmacy(self, pharmacy_id):
        """
        Возвращает все лекарства из указанной аптеки.
        :param pharmacy_id: ID аптеки
        :return: список кортежей
        """
        sql = f"SELECT * FROM {self.table_name()} WHERE pharmacy_id = %s ORDER BY drug_name"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (pharmacy_id,))
            return cur.fetchall()

    # ─────────────── Методы удаления ───────────────

    def delete_by_id(self, drug_id):
        """
        Удаляет лекарство по ID.
        :param drug_id: ID лекарства
        :return: количество удалённых строк (0 или 1)
        """
        sql = f"DELETE FROM {self.table_name()} WHERE drug_id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (drug_id,))
            self.dbconn.conn.commit()
            return cur.rowcount

    # ─────────────── Методы обновления ───────────────

    def update_by_id(self, drug_id, drug_name, dosage, quantity_or_volume,
                     manufacturer, instructions, requires_prescription, price, pharmacy_id):
        """
        Обновляет данные лекарства по уникальному ID.
        
        :param drug_id: ID лекарства (не изменяется)
        :param drug_name: новое название
        :param dosage: новая дозировка
        :param quantity_or_volume: количество/объём
        :param manufacturer: производитель
        :param instructions: инструкция
        :param requires_prescription: требует ли рецепта (True/False)
        :param price: цена (должна быть >= 0)
        :param pharmacy_id: ID аптеки
        :return: количество обновлённых строк (0 или 1)
        """
        sql = f"""
            UPDATE {self.table_name()}
            SET drug_name = %s,
                dosage = %s,
                quantity_or_volume = %s,
                manufacturer = %s,
                instructions = %s,
                requires_prescription = %s,
                price = %s,
                pharmacy_id = %s
            WHERE drug_id = %s
        """
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (
                drug_name, dosage, quantity_or_volume, manufacturer,
                instructions, requires_prescription, price, pharmacy_id, drug_id
            ))
            self.dbconn.conn.commit()
            return cur.rowcount

    # ─────────────── Метод вставки ───────────────

    def insert_one(self, drug_name, dosage, quantity_or_volume,
                   manufacturer, instructions, requires_prescription, price, pharmacy_id):
        """
        Вставляет новое лекарство в таблицу.
        Поле drug_id генерируется автоматически.
        
        :param pharmacy_id: ID аптеки, в которой есть лекарство
        :return: ID вставленного лекарства
        """
        cols = [
            "drug_name", "dosage", "quantity_or_volume", "manufacturer",
            "instructions", "requires_prescription", "price", "pharmacy_id"
        ]
        placeholders = ", ".join(["%s"] * len(cols))
        col_list = ", ".join(cols)
        sql = f"INSERT INTO {self.table_name()} ({col_list}) VALUES ({placeholders}) RETURNING drug_id"
        
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (
                drug_name, dosage, quantity_or_volume, manufacturer,
                instructions, requires_prescription, price, pharmacy_id
            ))
            self.dbconn.conn.commit()
            return cur.fetchone()[0]  # Возвращаем сгенерированный drug_id