import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLabel, QCheckBox, QSpinBox, \
    QPlainTextEdit
from PyQt5.QtGui import QPixmap


class KFC(QWidget):
    def __init__(self, names):
        super().__init__()
        self.initUI(names)

    def initUI(self, names):
        self.setGeometry(300, 150, 900, 700)
        self.setWindowTitle('KFC')
        self.out = []
        self.print_layout = QHBoxLayout()
        self.vbox = QVBoxLayout()
        for i in names:
            hbox = QHBoxLayout()
            self.cb = QCheckBox(i[0], self)
            self.cb.stateChanged.connect(self.cheker)
            hbox.addWidget(self.cb)
            price = QLabel(str(i[1]), self)
            hbox.addWidget(price)
            self.pixmap = QPixmap(i[2]).scaledToWidth(125)
            self.img = QLabel(self)
            self.img.setPixmap(self.pixmap)
            hbox.addWidget(self.img)
            exec("self.sb_{} = QSpinBox()".format(i[0]))
            exec("hbox.addWidget(self.sb_{})".format(i[0]))
            self.vbox.addLayout(hbox)
        self.input_window = QPlainTextEdit()
        self.input_window.setPlainText('')
        self.input_window.setEnabled(False)
        self.print_layout.addWidget(self.input_window)
        self.button = QPushButton("get a check")
        self.vbox.addWidget(self.button)
        self.button.clicked.connect(self.print)
        self.vbox.addLayout(self.print_layout)
        self.setLayout(self.vbox)

    def cheker(self, state):
        if self.cb.sender().isChecked():
            self.txt = self.cb.sender().text()
            for i in range(names.__len__()):
                if names[i][0] == self.txt:
                    self.out.append(i)
                    exec("self.sb_{}.setValue(1)".format(names[i][0]))

        else:
            self.txt = self.cb.sender().text()
            for i in range(names.__len__()):
                if names[i][0] == self.txt:
                    self.out.remove(i)
                    exec("self.sb_{}.setValue(0)".format(names[i][0]))

    def print(self):
        chk = ''
        count = 0
        for i in range(names.__len__()):
            exec("self.sb = self.sb_{}".format(names[i][0]))
            if self.sb.value() != 0 and i in self.out:
                chk += names[i][0] + ' x ' + str(self.sb.value()) + ' --- ' + str(self.sb.value() * names[i][1]) + '\n'
                count += self.sb.value() * names[i][1]
        chk += 'Total: ' + str(count)
        self.input_window.setPlainText(chk)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    names = [("name1", 100, "img1.jpg"), ("name2", 200, "img2.jpg"), ("name3", 300, "img3.jpg")]
    cl = KFC(names)
    cl.show()
    sys.exit(app.exec_())
