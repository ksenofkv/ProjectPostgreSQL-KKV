'''
Ксенофонтов Константин Владимирович
Вариант №22

Система управления лекарствами: категории и лекарства со связью.
Интерфейс использует только понятные пользователю данные (без ID).
'''
import sys

sys.path.append('tables')

from dbconnection import DbConnection
from project_config import ProjectConfig
from tables.drug_categories import DrugCategoriesTable
from tables.drugs import DrugsTable


class Main:

    config = ProjectConfig()
    connection = DbConnection(config)

    def __init__(self):
        from dbtable import DbTable
        DbTable.dbconn = self.connection

    def db_init(self):
        """Создаёт таблицы в правильном порядке."""
        categories = DrugCategoriesTable()
        drugs = DrugsTable()
        categories.create()
        drugs.create()

    def db_insert_somethings(self):
        """Заполняет таблицы тестовыми данными."""
        cat = DrugCategoriesTable()
        dr = DrugsTable()

        # Добавляем категории
        cat1_id = cat.insert_one(["Обезболивающие"])
        cat2_id = cat.insert_one(["Антибиотики"])

        # Добавляем лекарства
        dr.insert_one("Парацетамол", "500 мг", "20 таблеток", "Фармстандарт",
                      "Принимать по 1 таблетке каждые 6 часов", False, 50.00, cat1_id)
        dr.insert_one("Аспирин", "300 мг", "10 таблеток", "Байер",
                      "Перед едой", True, 120.50, cat1_id)
        dr.insert_one("Амоксициллин", "250 мг", "14 капсул", "Фармация",
                      "По назначению врача", True, 200.00, cat2_id)

    def db_drop(self):
        """Удаляет таблицы в обратном порядке."""
        drugs = DrugsTable()
        categories = DrugCategoriesTable()
        drugs.drop()
        categories.drop()

    def show_main_menu(self):
        menu = """\nДобро пожаловать в систему управления лекарствами!
Основное меню:
    1 - управление категориями;
    2 - сброс и инициализация таблиц;
    9 - выход."""
        print(menu)

    def read_next_step(self):
        return input("=> ").strip()

    def after_main_menu(self, next_step):
        if next_step == "2":
            self.db_drop()
            self.db_init()
            self.db_insert_somethings()
            print("\nТаблицы созданы заново!")
            return "0"
        elif next_step == "1":
            self.categories_menu()
            return "0"
        elif next_step == "9":
            return "9"
        else:
            print("\nНеверный выбор!")
            return "0"

    # ─────────────── РАБОТА С КАТЕГОРИЯМИ ───────────────

    def select_category_for_drugs(self):
        """Позволяет выбрать категорию для управления лекарствами."""
        cat_table = DrugCategoriesTable()
        categories = cat_table.all()
        if not categories:
            print("Нет категорий в базе.")
            return

        col_names = cat_table.column_names()
        id_idx = col_names.index("category_id")
        name_idx = col_names.index("category_name")

        print("\nСписок категорий:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat[name_idx]}")

        while True:
            choice = input("\nВыберите номер категории для работы с лекарствами (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(categories):
                cat = categories[int(choice) - 1]
                category_id = cat[id_idx]
                category_name = cat[name_idx]
                self.drugs_menu_for_category(category_id, category_name)
                return
            else:
                print("Неверный номер.")

    def add_category(self):
        """Добавляет новую категорию."""
        print("\nДобавление новой категории")
        name = input("Название категории: ").strip()
        if not name:
            print("Название обязательно!")
            return
        DrugCategoriesTable().insert_one([name])
        print("✅ Категория успешно добавлена!")

    def delete_category_by_number(self):
        """Удаляет категорию по номеру (с каскадным удалением лекарств)."""
        cat_table = DrugCategoriesTable()
        categories = cat_table.all()
        if not categories:
            print("Нет категорий в базе.")
            return

        col_names = cat_table.column_names()
        id_idx = col_names.index("category_id")
        name_idx = col_names.index("category_name")

        print("\nСписок категорий:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat[name_idx]}")

        while True:
            choice = input("\nВведите номер категории для удаления (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(categories):
                category_id = categories[int(choice) - 1][id_idx]
                try:
                    # Удаляем категорию (лекарства удалятся автоматически через CASCADE)
                    deleted = cat_table.delete_by_id(category_id)
                    if deleted > 0:
                        print(f"\n✅ Категория и все её лекарства удалены.")
                    else:
                        print("\n❌ Категория не найдена.")
                except Exception as e:
                    print(f"\n❌ Ошибка при удалении: {e}")
                return
            else:
                print("Неверный номер.")

    def categories_menu(self):
        """Меню управления категориями."""
        while True:
            print("\n--- Управление категориями ---")
            print("1 - выбрать категорию для работы с лекарствами")
            print("2 - добавить категорию")
            print("3 - удалить категорию")
            print("0 - назад в главное меню")
            choice = self.read_next_step()

            if choice == "1":
                self.select_category_for_drugs()
            elif choice == "2":
                self.add_category()
            elif choice == "3":
                self.delete_category_by_number()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    # ─────────────── РАБОТА С ЛЕКАРСТВАМИ В КОНТЕКСТЕ КАТЕГОРИИ ───────────────

    def drugs_menu_for_category(self, category_id, category_name):
        """Меню управления лекарствами для конкретной категории."""
        while True:
            print(f"\n--- Лекарства в категории: {category_name} ---")
            
            drugs_table = DrugsTable()
            drugs = drugs_table.find_by_category(category_id)

            if not drugs:
                print("В этой категории пока нет лекарств.")
            else:
                col_names = drugs_table.column_names()
                name_idx = col_names.index("drug_name")
                dosage_idx = col_names.index("dosage")
                qty_idx = col_names.index("quantity_or_volume")
                price_idx = col_names.index("price")

                for i, drug in enumerate(drugs, 1):
                    dosage = drug[dosage_idx] or ""
                    qty = drug[qty_idx] or ""
                    price = f"{float(drug[price_idx]):.2f}"
                    print(f"{i}. {drug[name_idx]} | Дозировка: {dosage} | Кол-во: {qty} | Цена: {price} руб.")

            print("\nОперации:")
            print("1 - добавить лекарство")
            print("2 - удалить лекарство")
            print("0 - назад")
            choice = self.read_next_step()

            if choice == "0":
                break
            elif choice == "1":
                self.add_drug_to_category(category_id)
            elif choice == "2":
                if drugs:
                    self.delete_drug_from_category(drugs)
                else:
                    print("Нет лекарств для удаления.")
            else:
                print("Неверный выбор.")

    def add_drug_to_category(self, category_id):
        """Добавляет лекарство в указанную категорию."""
        print("\nДобавление нового лекарства в категорию")
        
        name = input("Название: ").strip()
        if not name:
            print("Название обязательно!")
            return

        dosage = input("Дозировка (опционально): ").strip() or None
        qty = input("Количество/объём (опционально): ").strip() or None
        manufacturer = input("Производитель (опционально): ").strip() or None
        instructions = input("Инструкция (опционально): ").strip() or None

        while True:
            rx = input("Требует рецепта? (y/n): ").strip().lower()
            if rx in ('y', 'yes', '1'):
                requires_rx = True
                break
            elif rx in ('n', 'no', '0'):
                requires_rx = False
                break
            else:
                print("Введите y или n")

        while True:
            price_str = input("Цена (>=0): ").strip()
            try:
                price = float(price_str)
                if price < 0:
                    raise ValueError
                break
            except ValueError:
                print("Цена должна быть числом >= 0")

        try:
            DrugsTable().insert_one(
                name, dosage, qty, manufacturer, instructions, requires_rx, price, category_id
            )
            print("✅ Лекарство успешно добавлено!")
        except Exception as e:
            print(f"❌ Ошибка при добавлении: {e}")

    def delete_drug_from_category(self, drugs_list):
        """Удаляет лекарство по порядковому номеру."""
        drugs_table = DrugsTable()
        col_names = drugs_table.column_names()
        drug_id_idx = col_names.index("drug_id")

        while True:
            choice = input("\nВведите номер лекарства для удаления (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(drugs_list):
                drug_id = drugs_list[int(choice) - 1][drug_id_idx]
                deleted = DrugsTable().delete_by_id(drug_id)
                if deleted > 0:
                    print(f"\n✅ Лекарство №{choice} удалено.")
                else:
                    print("\n❌ Не удалось удалить лекарство.")
                return
            else:
                print("Неверный номер.")

    # ─────────────── ОСНОВНОЙ ЦИКЛ ───────────────

    def main_cycle(self):
        current_menu = "0"
        try:
            while current_menu != "9":
                if current_menu == "0":
                    self.show_main_menu()
                    next_step = self.read_next_step()
                    current_menu = self.after_main_menu(next_step)
            print("\nДо свидания!\n")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем (Ctrl+C)")
            print("\nДо свидания!\n")
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            print("\nДо свидания!\n")

    def test(self):
        return self.connection.test()


if __name__ == "__main__":
    m = Main()
    # m.test()
    m.main_cycle()