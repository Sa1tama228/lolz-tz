import sqlite3
import logging
from prettytable import PrettyTable

FEATURES = [
    'Удалить заметку: delete',
    'Добавить заметку: addnote',
    'Просмотреть все заметки: lk_notes',
    'Искать заметку: search'
]


class Database:
    def __init__(self, connect, program_active):
        logging.basicConfig(filename='app.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.connect = connect
        self.program_active = program_active
        self.cursor = connect.cursor()
        self._prepare_database()

    def _prepare_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notes(
            content TEXT NOT NULL,
            header TEXT NOT NULL)''')
        self.connect.commit()

    def _print_last_note(self, last_inserted_id):
        self.cursor.execute("SELECT * FROM Notes WHERE rowid = ?",
                            (last_inserted_id,))
        last_note = self.cursor.fetchone()
        table = PrettyTable(["Header", "Content"])
        table.add_row(last_note)
        print(f'заметка nr:{last_inserted_id}')

    def _look_notes(self):
        confirm = input("Уверены, что хотите вывести данные? yes/no: ").lower()
        if confirm == "yes":
            self.cursor.execute('''SELECT * FROM Notes''')
            data = self.cursor.fetchall()
            table = PrettyTable(["Header", "Content"])
            table.add_rows(data)
            print('Все заметки:')
            print(table)
        else:
            print("Ошибка, попробуйте снова.")
            logging.info("ошибка при вводе _look_notes()")

    def _search_note(self):
        target = input('Введите слово из заголовка/контента: ')
        self.cursor.execute('''
                SELECT * FROM Notes WHERE header LIKE ? OR content LIKE ?
            ''', ('%' + target + '%', '%' + target + '%'))
        search_results = self.cursor.fetchall()
        if search_results:
            table = PrettyTable(["Header", "Content"])
            table.add_rows(search_results)
            print('Результаты:')
            print(table)
        else:
            print('Не найдено заметок.')

    def _delete_note(self):
        keyword = input('Введите слово из заголовка/контента: ')
        try:
            self.cursor.execute("DELETE FROM Notes WHERE header LIKE ? "
                                "OR content LIKE ?",
                                ('%' + keyword + '%', '%' + keyword + '%'))
            self.connect.commit()
            print('Успешно удалено.')
            logging.info(f'Успешно удалил заметку по слову: {keyword}')
        except sqlite3.Error as e:
            print(f'Ошибка: {e}')
            logging.error(f'Ошибка при удалении заметки: {e}')

    def add_note_to_database(self):
        user_header = input('Заметка: ')
        user_note = input('Заголовок: ')
        self.cursor.execute("INSERT INTO Notes (header, content) "
                            "VALUES (?, ?)", (user_header, user_note))
        self.connect.commit()
        last_inserted_id = self.cursor.lastrowid
        print('Хотите просмотреть заметку? yes/no')
        user_want_check = input().lower()
        if user_want_check == "yes":
            self._print_last_note(last_inserted_id)
            logging.info(f"Новая заметка: {last_inserted_id}")
        else:
            print('Успешно сохранено.')
            logging.info(f"Новая заметка: {last_inserted_id}")

    def main(self):
        while self.program_active:
            print('Просмотрите документацию!')
            print('Команды: FEATURES')
            user_choice = input('Ваш выбор?: ').lower()

            if user_choice == 'addnote':
                self.add_note_to_database()

            elif user_choice == 'features':
                print(FEATURES)

            elif user_choice == "lk_notes":
                self._look_notes()

            elif user_choice == "search":
                self._search_note()

            elif user_choice == 'delete':
                print('This command deletes a note by keyword')
                sure = input('Уверены, что хотите удалить заметку? yes/no: ')
                if sure == "yes":
                    self._delete_note()

            else:
                print('Ошибка при вводе, попробуйте снова')


if __name__ == '__main__':
    db = Database(
        connect=sqlite3.connect('files/Database.db'),  # db name
        program_active=True)
    db.main()
