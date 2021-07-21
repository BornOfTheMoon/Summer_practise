import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore, QtWidgets
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.params = {}
        self.con = sqlite3.connect("films.db")
        self.setGeometry(700, 100, 750, 700)
        self.setWindowTitle("Films")
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(20, 10, 160, 20))
        self.select_genres()
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(630, 10, 90, 20)
        self.pushButton.setText("Find")
        self.pushButton.clicked.connect(self.select)
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10, 40, 730, 630))

    def select_genres(self):
        req = "SELECT * from genres"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall():
            self.params[key] = value
        self.comboBox.addItems(list(self.params.keys()))

    def select(self):
        req = "SELECT * FROM Films WHERE genre = {}".format(self.params.get(self.comboBox.currentText()))
        cur = self.con.cursor()
        result = cur.execute(req).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())
