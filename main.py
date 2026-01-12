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
        # Устанавливаем соединение для всех таблиц
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

        # Добавляем аптеки
        ph1_id = ph.insert_one(["ул. Ленина, 10", "+74951234567", "Охотный Ряд"])
        ph2_id = ph.insert_one(["пр. Мира, 25", "+74959876543", "Комсомольская"])

        # Добавляем лекарства, привязанные к аптекам
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
    1 - просмотр лекарств;
    2 - управление аптеками;
    3 - сброс и инициализация таблиц;
    9 - выход."""
        print(menu)

    def read_next_step(self):
        return input("=> ").strip()

    def after_main_menu(self, next_step):
        if next_step == "3":
            self.db_drop()
            self.db_init()
            self.db_insert_somethings()
            print("\nТаблицы созданы заново!")
            return "0"
        elif next_step == "2":
            self.pharmacy_menu()
            return "0"
        elif next_step == "1":
            return "1"
        elif next_step == "9":
            return "9"
        else:
            print("\nВыбрано неверное число! Повторите ввод!")
            return "0"

    # ─────────────── РАБОТА С АПТЕКАМИ ───────────────

    def show_pharmacies(self):
        """Показывает список аптек с порядковыми номерами. Возвращает список записей."""
        print("\nСписок аптек:")
        ph_table = PharmaciesTable()
        pharmacies = ph_table.all()

        if not pharmacies:
            print("Нет аптек в базе.")
            return []

        for i, ph in enumerate(pharmacies, 1):
            print(f"{i}. Адрес: {ph[1]} | Телефон: {ph[2]} | Метро: {ph[3]}")
        return pharmacies

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
        pharmacies = self.show_pharmacies()
        if not pharmacies:
            return

        while True:
            choice = input("\nВведите номер аптеки для удаления (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(pharmacies):
                pharmacy_id = pharmacies[int(choice) - 1][0]  # id из записи
                ph_table = PharmaciesTable()
                ph_table.delete_with_drugs(pharmacy_id)
                print(f"\n✅ Аптека №{choice} и все её лекарства удалены.")
                return
            else:
                print("Неверный номер. Попробуйте снова.")

    def edit_pharmacy_by_number(self):
        """Редактирует аптеку по порядковому номеру."""
        pharmacies = self.show_pharmacies()
        if not pharmacies:
            return

        while True:
            choice = input("\nВведите номер аптеки для редактирования (0 - отмена): ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(pharmacies):
                ph = pharmacies[int(choice) - 1]
                pharmacy_id = ph[0]

                print(f"\nРедактирование аптеки №{choice}")
                new_address = input(f"Новый адрес ({ph[1]}): ").strip() or ph[1]
                new_phone = input(f"Новый телефон ({ph[2]}): ").strip() or ph[2]
                new_metro = input(f"Новое метро ({ph[3]}): ").strip() or ph[3]

                ph_table = PharmaciesTable()
                # ИСПРАВЛЕНО: используем существующий метод update_by_id
                ph_table.update_by_id(pharmacy_id, new_address, new_phone, new_metro)
                print("\n✅ Аптека успешно обновлена!")
                return
            else:
                print("Неверный номер.")

    def pharmacy_menu(self):
        """Меню управления аптеками."""
        while True:
            print("\n--- Управление аптеками ---")
            print("1 - просмотр списка аптек")
            print("2 - добавить аптеку")
            print("3 - удалить аптеку")
            print("4 - редактировать аптеку")
            print("0 - назад в главное меню")
            choice = self.read_next_step()

            if choice == "1":
                self.show_pharmacies()
            elif choice == "2":
                self.add_pharmacy()
            elif choice == "3":
                self.delete_pharmacy_by_number()
            elif choice == "4":
                self.edit_pharmacy_by_number()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    # ─────────────── РАБОТА С ЛЕКАРСТВАМИ ───────────────

    def show_drugs(self):
        """Просмотр списка лекарств."""
        print("\nПросмотр списка лекарств!")

        drugs_table = DrugsTable()
        lst = drugs_table.all()
        if not lst:
            print("Нет лекарств в базе.")
            menu = """\nДальнейшие операции:
    0 - возврат в главное меню;
    9 - выход."""
            print(menu)
            return

        # Получаем список имён колонок
        col_names = drugs_table.column_names()
        
        # Находим индексы нужных колонок
        drug_name_idx = col_names.index("drug_name")
        dosage_idx = col_names.index("dosage")
        qty_idx = col_names.index("quantity_or_volume")
        manuf_idx = col_names.index("manufacturer")
        price_idx = col_names.index("price")
        pharmacy_id_idx = col_names.index("pharmacy_id")

        # Получаем названия аптек
        ph_table = PharmaciesTable()
        pharmacies = {row[0]: row[1] for row in ph_table.all()}  # {id: address}

        # Вычисляем ширину колонок
        max_name = max(len(str(row[drug_name_idx])) for row in lst)
        max_dosage = max(len(str(row[dosage_idx] or "")) for row in lst)
        max_qty = max(len(str(row[qty_idx] or "")) for row in lst)
        max_manuf = max(len(str(row[manuf_idx] or "")) for row in lst)
        max_pharmacy = max(len(pharmacies.get(row[pharmacy_id_idx], "—")) for row in lst)
        max_price = max(len(f"{float(row[price_idx]):.2f}") for row in lst)

        col_widths = {
            'name': max(max_name, len('Название')) + 2,
            'dosage': max(max_dosage, len('Дозировка')) + 2,
            'qty': max(max_qty, len('Кол-во/Объём')) + 2,
            'manuf': max(max_manuf, len('Производитель')) + 2,
            'pharmacy': max(max_pharmacy, len('Аптека')) + 2,
            'price': max(max_price, len('Цена')) + 2,
        }

        header = (
            f"{'Название':<{col_widths['name']}}"
            f"{'Дозировка':<{col_widths['dosage']}}"
            f"{'Кол-во/Объём':<{col_widths['qty']}}"
            f"{'Производитель':<{col_widths['manuf']}}"
            f"{'Аптека':<{col_widths['pharmacy']}}"
            f"{'Цена':<{col_widths['price']}}"
        )
        print(f'\n{header}')
        print("-" * len(header))

        for row in lst:
            pharmacy_addr = pharmacies.get(row[pharmacy_id_idx], "—")
            price_str = f"{float(row[price_idx]):.2f}"
            print(
                f"{row[drug_name_idx]:<{col_widths['name']}}"
                f"{(row[dosage_idx] or ''):<{col_widths['dosage']}}"
                f"{(row[qty_idx] or ''):<{col_widths['qty']}}"
                f"{(row[manuf_idx] or ''):<{col_widths['manuf']}}"
                f"{pharmacy_addr:<{col_widths['pharmacy']}}"
                f"{price_str}".ljust(col_widths['price'])
            )

        menu = """\nДальнейшие операции:
    0 - возврат в главное меню;
    9 - выход."""
        print(menu)

    def after_show_drugs(self, next_step):
        if next_step not in ("0", "9"):
            print("\nНеверный выбор!")
            return "1"
        return next_step

    # ─────────────── ОСНОВНОЙ ЦИКЛ ───────────────

    def main_cycle(self):
        current_menu = "0"
        try:
            while current_menu != "9":
                if current_menu == "0":
                    self.show_main_menu()
                    next_step = self.read_next_step()
                    current_menu = self.after_main_menu(next_step)
                elif current_menu == "1":
                    self.show_drugs()
                    next_step = self.read_next_step()
                    current_menu = self.after_show_drugs(next_step)
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


# Запуск программы
if __name__ == "__main__":
    m = Main()
    # m.test()  # Раскомментируйте для теста подключения
    m.main_cycle()