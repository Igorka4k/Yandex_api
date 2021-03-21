import sys

from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import requests
import io


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.initUI()

    def initUI(self):
        url = "https://static-maps.yandex.ru/1.x/?ll=134.590649,-23.519879&spn=35.5,35.5&l=sat"
        response = requests.get(url)
        bytes = io.BytesIO(response.content)
        self.draw(bytes)

    def draw(self, bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(bytes.read())
        self.label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())