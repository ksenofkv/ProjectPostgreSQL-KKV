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