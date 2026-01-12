'''
Ксенофонтов Константин Владимирович
Вариант №22

Система управления аптекой: аптеки и лекарства со связью.
Интерфейс использует только понятные пользователю данные (без ID).
'''
import sys

sys.path.append('tables')

from dbconnection import DbConnection
from project_config import ProjectConfig
from tables.pharmacies import PharmaciesTable
from tables.drugs import DrugsTable


class Main:

    config = ProjectConfig()
    connection = DbConnection(config)

    def __init__(self):
        from dbtable import DbTable
        DbTable.dbconn = self.connection

    def db_init(self):
        """Создаёт таблицы в правильном порядке."""
        pharmacies = PharmaciesTable()
        drugs = DrugsTable()
        pharmacies.create()
        drugs.create()

    def db_insert_somethings(self):
        """Заполняет таблицы тестовыми данными с привязкой лекарств к аптекам."""
        ph = PharmaciesTable()
        dr = DrugsTable()

        ph1_id = ph.insert_one(["ул. Ленина, 10", "+74951234567", "Охотный Ряд"])
        ph2_id = ph.insert_one(["пр. Мира, 25", "+74959876543", "Комсомольская"])

        dr.insert_one("Парацетамол", "500 мг", "20 таблеток", "Фармстандарт",
                      "Принимать по 1 таблетке каждые 6 часов", False, 50.00, ph1_id)
        dr.insert_one("Аспирин", "300 мг", "10 таблеток", "Байер",
                      "Перед едой", True, 120.50, ph1_id)
        dr.insert_one("Нурофен", "200 мг", "16 таблеток", "Reckitt",
                      "При боли", False, 85.00, ph2_id)

    def db_drop(self):
        """Удаляет таблицы в обратном порядке."""
        drugs = DrugsTable()
        pharmacies = PharmaciesTable()
        drugs.drop()
        pharmacies.drop()

    def show_main_menu(self):
        menu = """\nДобро пожаловать в систему управления аптекой!
Основное меню:
    1 - управление аптеками;
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
            self.pharmacy_menu()
            return "0"
        elif next_step == "9":
            return "9"
        else:
            print("\nНеверный выбор!")
            return "0"

    # ─────────────── РАБОТА С АПТЕКАМИ ───────────────

    def show_pharmacies_list(self):
        """Показывает только список аптек без возврата данных."""
        ph_table = PharmaciesTable()
        pharmacies = ph_table.all()
        if not pharmacies:
            print("Нет аптек в базе.")
            return

        col_names = ph_table.column_names()
        addr_idx = col_names.index("address")
        phone_idx = col_names.index("phone_number")
        metro_idx = col_names.index("nearest_metro_station")

        print("\nСписок аптек:")
        for i, ph in enumerate(pharmacies, 1):
            print(f"{i}. Адрес: {ph[addr_idx]} | Телефон: {ph[phone_idx]} | Метро: {ph[metro_idx]}")

    def add_pharmacy(self):
        """Добавляет новую аптеку."""
        print("\nДобавление новой аптеки")
        address = input("Адрес: ").strip()
        phone = input("Телефон: ").strip()
        metro = input("Ближайшее метро: ").strip()

        if not all([address, phone, metro]):
            print("Все поля обязательны!")
            return

        PharmaciesTable().insert_one([address, phone, metro])
        print("✅ Аптека успешно добавлена!")

    def delete_pharmacy_by_number(self):
        """Удаляет аптеку по порядковому номеру (с каскадным удалением лекарств)."""
        ph_table = PharmaciesTable()
        pharmacies = ph_table.all()
        if not pharmacies:
            print("Нет аптек в базе.")
            return

        col_names = ph_table.column_names()
        id_idx = col_names.index("id")
        addr_idx = col_names.index("address")
        phone_idx = col_names.index("phone_number")
        metro_idx = col_names.index("nearest_metro_station")

        print("\nСписок аптек:")
        for i, ph in enumerate(pharmacies, 1):
            print(f"{i}. Адрес: {ph[addr_idx]} | Телефон: {ph[phone_idx]} | Метро: {ph[metro_idx]}")

        while True:
            choice = input("\nВведите номер аптеки для удаления (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(pharmacies):
                pharmacy_id = pharmacies[int(choice) - 1][id_idx]
                ph_table.delete_with_drugs(pharmacy_id)
                print(f"\n✅ Аптека №{choice} и все её лекарства удалены.")
                return
            else:
                print("Неверный номер. Попробуйте снова.")

    def edit_pharmacy_by_number(self):
        """Редактирует аптеку по порядковому номеру."""
        ph_table = PharmaciesTable()
        pharmacies = ph_table.all()
        if not pharmacies:
            print("Нет аптек в базе.")
            return

        col_names = ph_table.column_names()
        id_idx = col_names.index("id")
        addr_idx = col_names.index("address")
        phone_idx = col_names.index("phone_number")
        metro_idx = col_names.index("nearest_metro_station")

        print("\nСписок аптек:")
        for i, ph in enumerate(pharmacies, 1):
            print(f"{i}. Адрес: {ph[addr_idx]} | Телефон: {ph[phone_idx]} | Метро: {ph[metro_idx]}")

        while True:
            choice = input("\nВведите номер аптеки для редактирования (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(pharmacies):
                ph = pharmacies[int(choice) - 1]
                pharmacy_id = ph[id_idx]

                print(f"\nРедактирование аптеки №{choice}")
                new_address = input(f"Новый адрес ({ph[addr_idx]}): ").strip() or ph[addr_idx]
                new_phone = input(f"Новый телефон ({ph[phone_idx]}): ").strip() or ph[phone_idx]
                new_metro = input(f"Новое метро ({ph[metro_idx]}): ").strip() or ph[metro_idx]

                ph_table.update_by_id(pharmacy_id, new_address, new_phone, new_metro)
                print("\n✅ Аптека успешно обновлена!")
                return
            else:
                print("Неверный номер.")

    def select_pharmacy_for_drugs(self):
        """Позволяет выбрать аптеку для управления лекарствами."""
        ph_table = PharmaciesTable()
        pharmacies = ph_table.all()
        if not pharmacies:
            print("Нет аптек в базе.")
            return

        col_names = ph_table.column_names()
        id_idx = col_names.index("id")
        addr_idx = col_names.index("address")
        phone_idx = col_names.index("phone_number")
        metro_idx = col_names.index("nearest_metro_station")

        print("\nСписок аптек:")
        for i, ph in enumerate(pharmacies, 1):
            print(f"{i}. Адрес: {ph[addr_idx]} | Телефон: {ph[phone_idx]} | Метро: {ph[metro_idx]}")

        while True:
            choice = input("\nВыберите номер аптеки для работы с лекарствами (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(pharmacies):
                ph = pharmacies[int(choice) - 1]
                pharmacy_id = ph[id_idx]
                pharmacy_address = ph[addr_idx]
                self.drugs_menu_for_pharmacy(pharmacy_id, pharmacy_address)
                return
            else:
                print("Неверный номер.")

    def pharmacy_menu(self):
        """Меню управления аптеками."""
        while True:
            print("\n--- Управление аптеками ---")
            print("1 - выбрать аптеку для работы с лекарствами")
            print("2 - просмотр списка аптек")
            print("3 - добавить аптеку")
            print("4 - удалить аптеку")
            print("5 - редактировать аптеку")
            print("0 - назад в главное меню")
            choice = self.read_next_step()

            if choice == "1":
                self.select_pharmacy_for_drugs()
            elif choice == "2":
                self.show_pharmacies_list()
            elif choice == "3":
                self.add_pharmacy()
            elif choice == "4":
                self.delete_pharmacy_by_number()
            elif choice == "5":
                self.edit_pharmacy_by_number()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    # ─────────────── РАБОТА С ЛЕКАРСТВАМИ В КОНТЕКСТЕ АПТЕКИ ───────────────

    def drugs_menu_for_pharmacy(self, pharmacy_id, pharmacy_address):
        """Меню управления лекарствами для конкретной аптеки."""
        while True:
            print(f"\n--- Лекарства в аптеке: {pharmacy_address} ---")
            
            drugs_table = DrugsTable()
            drugs = drugs_table.find_by_pharmacy(pharmacy_id)

            if not drugs:
                print("В этой аптеке пока нет лекарств.")
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
                self.add_drug_to_pharmacy(pharmacy_id)
            elif choice == "2":
                if drugs:
                    self.delete_drug_from_pharmacy(drugs)
                else:
                    print("Нет лекарств для удаления.")
            else:
                print("Неверный выбор.")

    def add_drug_to_pharmacy(self, pharmacy_id):
        """Добавляет лекарство в указанную аптеку."""
        print("\nДобавление нового лекарства в аптеку")
        
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
                name, dosage, qty, manufacturer, instructions, requires_rx, price, pharmacy_id
            )
            print("✅ Лекарство успешно добавлено!")
        except Exception as e:
            print(f"❌ Ошибка при добавлении: {e}")

    def delete_drug_from_pharmacy(self, drugs_list):
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
        from dbtable import DbTable
        return DbTable.dbconn.test()


if __name__ == "__main__":
    m = Main()
    # m.test()
    m.main_cycle()