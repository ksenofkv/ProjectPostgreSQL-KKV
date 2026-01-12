import os
import yaml

class ProjectConfig:
    """Класс считывает базовые настройки из файла config.yaml"""

    def __init__(self):
        # Получаем путь к директории, где лежит этот файл (project_config.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.yaml')
        
        # Читаем конфигурацию
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.dbname = config['dbname']
            self.user = config['user']
            self.password = config['password']
            self.host = config['host']
            self.dbtableprefix = config['dbtableprefix']

# Этот блок запускается только при прямом запуске файла
if __name__ == "__main__":
    x = ProjectConfig()
    # Выводим один из существующих атрибутов, например dbname
    print("Database name:", x.dbname)
    # Или можно вывести всё:
    print({
        'dbname': x.dbname,
        'user': x.user,
        'host': x.host,
        'dbtableprefix': x.dbtableprefix
    })
    
