from dbtable import DbTable

class DrugCategoriesTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "drug_categories"

    def columns(self):
        return {
            "category_id": ["serial", "PRIMARY KEY"],
            "category_name": ["varchar(255)", "NOT NULL", "UNIQUE"]
        }

    def primary_key(self):
        return ['category_id']

    def column_names_without_id(self):
        """Исключаем category_id из INSERT."""
        return ["category_name"]

    def insert_one(self, vals):
        """Вставляет новую категорию.
        :param vals: список [category_name]
        :return: category_id
        """
        if len(vals) != 1:
            raise ValueError("Ожидается ровно 1 значение: [category_name]")
        sql = f"INSERT INTO {self.table_name()} (category_name) VALUES (%s) RETURNING category_id"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, vals)
            self.dbconn.conn.commit()
            return cur.fetchone()[0]

    def delete_by_id(self, category_id):
        """Удаляет категорию по ID.
        :param category_id: ID категории
        :return: количество удалённых строк (0 или 1)
        """
        sql = f"DELETE FROM {self.table_name()} WHERE category_id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (category_id,))
            self.dbconn.conn.commit()
            return cur.rowcount

    def find_by_id(self, category_id):
        """
        Находит категорию по ID.
        :param category_id: ID категории
        :return: кортеж с данными или None, если не найдено
        """
        sql = f"SELECT * FROM {self.table_name()} WHERE category_id = %s"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql, (category_id,))
            return cur.fetchone()