import sys

from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QPlainTextEdit, QTextBrowser


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.text = QPlainTextEdit(self)
        self.text.setGeometry(50, 50, 700, 300)

        self.btn = QPushButton('push', self)
        self.btn.move(370, 400)
        self.btn.resize(self.btn.sizeHint())

        self.btn.clicked.connect(self.to_html)

    def initUI(self):
        self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle('Form')

    def to_html(self):
        self.t = QTextBrowser()
        self.t.setHtml(self.text.toPlainText())
        self.t.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fr = Form()
    fr.show()
    sys.exit(app.exec_())
