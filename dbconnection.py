# Установка соединения с базой данных
# (параметры передаются через класс конфиг).
import psycopg2
from psycopg2 import sql

class DbConnection:
    def __init__(self, config):
        self.dbname = config.dbname
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.prefix = config.dbtableprefix

        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
        except psycopg2.OperationalError as e:
            raise RuntimeError(f"Ошибка подключения к базе данных: {e}")

    def close(self):
        """Явное закрытие соединения."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def test(self):
        """Проверка работоспособности соединения."""
        with self.conn.cursor() as cur:
            # Используем временную таблицу — она автоматически удалится
            cur.execute("CREATE TEMP TABLE test_conn(test integer)")
            cur.execute("INSERT INTO test_conn(test) VALUES(1)")
            self.conn.commit()
            cur.execute("SELECT * FROM test_conn")
            result = cur.fetchall()

        # Проверяем результат
        if not result:
            return False
        return result[0][0] == 1
    

    # Только для тестирования при прямом запуске
if __name__ == "__main__":
    from project_config import ProjectConfig

    try:
        config = ProjectConfig()
        db = DbConnection(config)
        print("✅ Подключение установлено.")
        print("🧪 Тест соединения:", "OK" if db.test() else "FAIL")
        db.close()
        print("🔌 Соединение закрыто.")
    except Exception as e:
        print("❌ Ошибка:", e)


