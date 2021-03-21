import sys

from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import io


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.latitude = '0.0'
        self.longitude = '0.0'
        self.lineEdit.setText("35.35")
        self.lineEdit_2.setText("35.35")
        self.spn = self.spn = self.lineEdit_3.setText('1.0')
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.fetchImage)

    def fetchImage(self):
        self.latitude = self.lineEdit.text()
        self.longitude = self.lineEdit_2.text()
        self.spn = self.lineEdit_3.text()
        url = f"https://static-maps.yandex.ru/1.x/?ll={self.latitude},{self.longitude}&spn={self.spn},{self.spn}&l=sat"
        self.draw(url)

    def draw(self, url):
        response = requests.get(url)
        bytes = io.BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(bytes.read())
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        try:
            float(self.spn)
        except Exception:
            self.spn = 0
        try:
            float(self.lineEdit.text())
        except Exception:
            self.lineEdit.setText('35.35')
        try:
            float(self.lineEdit.text())
        except Exception:
            self.lineEdit.setText("35.35")
        if event.key() == Qt.Key_PageUp:
            n = min(float(self.spn) + 0.5, 90)
            self.lineEdit_3.setText(str(n))
        if event.key() == Qt.Key_PageDown:
            n = max(float(self.spn) - 0.5, 0.5)
            self.lineEdit_3.setText(str(n))

        if event.key() == Qt.Key_W:
            n = float(self.lineEdit_2.text()) + float(self.spn)
            self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_S:
            n = float(self.lineEdit_2.text()) - float(self.spn)
            self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_A:
            n = float(self.lineEdit.text()) - float(self.spn)
            self.lineEdit.setText(str(n))

        if event.key() == Qt.Key_D:
            n = float(self.lineEdit.text()) + float(self.spn)
            self.lineEdit.setText(str(n))
        self.fetchImage()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
