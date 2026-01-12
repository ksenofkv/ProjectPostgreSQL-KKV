import yaml
#
# with open('config.yaml', encoding='utf-8') as f:
#     config = yaml.safe_load(f)
#
# print(config)
#
# from project_config import ProjectConfig
#
# config = ProjectConfig()
#
# for key in ['dbname', 'user', 'password', 'host', 'dbtableprefix']:
#     val = getattr(config, key)
#     print(f"{key!r}: {val!r}, len={len(val)}")
#
# import sys
# print(sys.getdefaultencoding())   # Должно вывести 'utf-8'
# print(sys.stdout.encoding)        # Должно быть 'UTF-8'

# with open("config.yaml", "rb") as f:
#     data = f.read()
#     print(data)
#
# print("DSN repr =", repr(dsn))

# test_connection.py
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="DZ1-3",
        user="postgres",
        password="12345678",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("Подключение успешно, результат теста:", cur.fetchone())
    conn.close()
except Exception as e:
    print("Ошибка подключения:", e)
