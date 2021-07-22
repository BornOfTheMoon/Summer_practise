from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import sqlite3

FIELDS = ('Идентификатор', 'Название', 'Год', 'Жанр', 'Продолжительность')
DB_FIELDS = ('id', 'title', 'year', 'genre', 'duration')
ID_POSITION = 0
GENRE_POSITION = 3
DIF_FOR_GENRES_ID = 3
DIF_FOR_FILMS_ID = 6000


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.table = TableWidget(self)
        self.form = NewFilmForm(self)
        self.stacked_widget = QStackedWidget()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setGeometry(500, 100, 1000, 600)

        self.stacked_widget.addWidget(self.table)
        self.stacked_widget.addWidget(self.form)
        self.stacked_widget.setCurrentWidget(self.table)

        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def switch_to_form(self):
        self.stacked_widget.setCurrentWidget(self.form)

    def switch_to_table(self):
        self.stacked_widget.setCurrentWidget(self.table)


class TableWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.combobox = QComboBox()
        self.table = FilmsTable(self)

        self.save_button = QPushButton("Сохранить")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.combobox.addItems(FIELDS)
        self.combobox.activated[str].connect(self.chosen_field_catcher)
        self.table.setMinimumSize(800, 600)
        self.save_button.clicked.connect(self.table.connection.commit)
        self.add_button.clicked.connect(self.parent.switch_to_form)
        self.delete_button.clicked.connect(self.table.delete)
        main_layout.addWidget(self.combobox)
        main_layout.addWidget(self.table)
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self.add_button)
        lower_layout.addWidget(self.save_button)
        lower_layout.addWidget(self.delete_button)
        main_layout.addLayout(lower_layout)
        self.setLayout(main_layout)

    def chosen_field_catcher(self, text):
        if text in ('Идентификатор', 'Год', 'Продолжительность'):
            i, ok_pressed = QInputDialog.getInt(self, text, 'Введите {} для выборки'.format(text))
            if ok_pressed:
                self.table.search_in_table(text, i)

        elif text in ('Жанр', 'Название'):
            i, ok_pressed = QInputDialog.getText(self, text, 'Введите {} для выборки'.format(text))
            if ok_pressed:
                self.table.search_in_table(text, i)

    def add(self, data):
        self.table.add(data)


class FilmsTable(QWidget):
    def __init__(self, parent, db_name='films.db'):
        super().__init__()
        self.parent = parent
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.table = QTableWidget()
        self.queue = list()
        self.field = str()
        self.value = str()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def search_in_table(self, field, value):
        self.field = field
        self.value = value
        films = list(self.make_the_request(field, value))[0]
        if len(films) > 0:
            self.table.setColumnCount(len(films[0]))
        self.table.setHorizontalHeaderLabels(FIELDS)
        self.table.setRowCount(0)
        for i, row in enumerate(films):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, element in enumerate(row):
                if j == GENRE_POSITION:
                    element = list(
                        self.cursor.execute("""SELECT title FROM genres WHERE id=?""", (element,)).fetchone()).pop()

                item = QTableWidgetItem(str(element))
                if j == ID_POSITION:
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(i, j, item)

        self.table.itemChanged.connect(self.changes_catcher)
        self.table.itemClicked.connect(self.add_to_delete_queue)

        self.table.resizeColumnsToContents()

    def make_the_request(self, field, value, quantity=30):
        relations = {
            'Идентификатор': """SELECT * FROM FILMS WHERE id = ?""",
            'Название': """SELECT * FROM FILMS WHERE title like ?""",
            'Год': """SELECT * FROM FILMS WHERE year = ?""",
            'Продолжительность': """SELECT * FROM FILMS WHERE duration = ?""",
            'Жанр': """SELECT * FROM FILMS
                            WHERE genre=(
                        SELECT id FROM genres
                            WHERE title like ?)"""
        }
        if field == 'Название':
            value += '%'
        return self.cursor.execute(relations[field], (value,)).fetchmany(quantity), relations[field], value

    def changes_catcher(self, item: QTableWidgetItem):
        film_id = int(self.table.item(item.row(), 0).text())
        field = list(DB_FIELDS)[item.column()]
        request = """UPDATE Films
                  SET {} = ?
                  WHERE id = {}""".format(field, film_id)

        if item.column() in (2, 4):
            try:
                self.cursor.execute(request, (int(item.text()),))
            except:
                self.cursor.execute(request, (0,))
        elif item.column() == 1:
            self.cursor.execute(request, (item.text(),)).fetchone()
        elif item.column() == 3:
            wrapped_id_of_genre = self.cursor.execute("""SELECT id
                                                         FROM genres
                                                         WHERE title = ?""", (item.text(),)).fetchone()

            if not wrapped_id_of_genre:
                count = list(self.cursor.execute("""SELECT COUNT(*) FROM genres""").fetchone())[0] + 3
                self.cursor.execute("""INSERT INTO genres(id,title) VALUES(?, ?)""", (count, item.text()))
                self.cursor.execute("""UPDATE Films
                                        SET genre = ?
                                        WHERE id = {}""".format(film_id), (count,))

            else:
                self.cursor.execute("""UPDATE Films
                                       SET genre = ?
                                       WHERE id = {}""".format(film_id), (list(wrapped_id_of_genre)[0],))

    def add(self, data):
        id_of_genre = self.cursor.execute("""SELECT id 
                                             FROM genres 
                                             WHERE title = ?""", (data['genre'],)).fetchone()
        if not id_of_genre:
            id_of_genre = list(self.cursor.execute("""SELECT COUNT(*) FROM genres""").fetchone())[0] + DIF_FOR_GENRES_ID
            self.cursor.execute("""INSERT INTO genres(id,title) VALUES(?, ?)""", (id_of_genre, data['genre']))
            self.connection.commit()
        else:
            id_of_genre = list(id_of_genre)[0]
        film_id = list(self.cursor.execute("""SELECT COUNT(*) FROM Films""").fetchone())[0] + DIF_FOR_FILMS_ID
        self.cursor.execute("""INSERT INTO Films(id,title,year,genre,duration) VALUES (?, ?, ?, ?, ?)""",
                            (film_id, data["title"], data["year"], id_of_genre, data["duration"]))
        self.connection.commit()
        item = QTableWidgetItem(film_id)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)

        self.search_in_table(FIELDS[1], data["title"])

    def add_to_delete_queue(self, item):
        req = ("", "")
        if item.column() in (2, 4):
            try:
                req = ("""DELETE from Films
                                where {} like ?""".format(DB_FIELDS[item.column()]), int(item.text()))
            except:
                pass
        elif item.column() == 3:
            id_of_genre = list(self.cursor.execute("""SELECT id
                                                 FROM genres
                                                 WHERE title = ?""", (item.text(),)).fetchone())[0]
            req = ("""DELETE from Films
                                where {} = ?""".format(DB_FIELDS[item.column()]), id_of_genre)
        else:
            req = ("""DELETE from Films 
                    where {} = ?""".format(DB_FIELDS[item.column()]), item.text())

        if req != ("", "") and req not in self.queue:
            self.queue.append(req)
        elif req in self.queue:
            self.queue.remove(req)

    def delete(self):
        for req in self.queue:
            indexed_req = list(req)
            self.cursor.execute(indexed_req[0], (indexed_req[1], ))
        self.queue = list()
        self.connection.commit()
        self.search_in_table(self.field, self.value)


class NewFilmForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title = QLineEdit()
        self.genre = QLineEdit()
        self.duration = QSpinBox()
        self.duration.setMaximum(1000)
        self.year = QSpinBox()
        self.year.setMaximum(2021)
        self.submit_button = QPushButton("Добавить")
        self.cancel_button = QPushButton("Отмена")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.submit_button.clicked.connect(self.add_film)
        self.cancel_button.clicked.connect(self.parent.switch_to_table)
        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.title)
        layout.addWidget(QLabel("Жанр"))
        layout.addWidget(self.genre)
        layout.addWidget(QLabel("Год"))
        layout.addWidget(self.year)
        layout.addWidget(QLabel("Продолжительность"))
        layout.addWidget(self.duration)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def add_film(self):
        res = {
            'title': self.title.text(),
            'genre': self.genre.text(),
            'year': self.year.value(),
            'duration': self.duration.value()
        }
        self.parent.table.add(res)
        self.year.setValue(0)
        self.duration.setValue(0)
        self.title.setText("")
        self.genre.setText("")
        self.parent.switch_to_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec())
