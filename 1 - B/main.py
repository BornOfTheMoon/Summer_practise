import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QLabel


class Calc(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 150, 300, 200)
        self.setWindowTitle('Calculator')
        grid = QGridLayout()
        self.setLayout(grid)

        names = ['Clr', 'Bck', '(', ')',
                 '7', '8', '9', '/',
                 '4', '5', '6', '*',
                 '1', '2', '3', '-',
                 '0', '.', '=', '+']

        self.t = QLabel("empty")
        grid.addWidget(self.t, 0, 1, 1, 2)
        positions = [(i, j) for i in range(1, 6) for j in range(4)]
        for position, name in zip(positions, names):
            if name == '':
                continue
            button = QPushButton(name)
            grid.addWidget(button, *position)
            button.clicked.connect(self.receive)

    def receive(self):
        bt = self.sender()
        if bt.text() == 'Clr':
            self.t.setText('empty')
        elif bt.text() == 'Bck':
            if self.t.text() == 'error':
                self.t.setText('empty')
            if self.t.text() != 'empty':
                cur_t = self.t.text()
                self.t.setText(cur_t[:-1])
            if self.t.text() == '':
                self.t.setText('empty')
        elif bt.text() != '=':
            cur_t = self.t.text()
            if self.t.text() == 'empty' or self.t.text() == 'error':
                self.t.setText(bt.text())
            else:
                self.t.setText(cur_t + bt.text())
        else:
            try:
                answer = str(eval(self.t.text()))
            except:
                answer = 'error'
            self.t.setText(answer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cl = Calc()
    cl.show()
    sys.exit(app.exec_())
