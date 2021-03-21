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
        self.pushButton.clicked.connect(self.fetchImage)

    def fetchImage(self):
        latitude = self.lineEdit.text()
        longitude = self.lineEdit_2.text()
        spn = self.lineEdit_3.text()
        url = f"https://static-maps.yandex.ru/1.x/?ll={latitude},{longitude}&spn={spn},{spn}&l=sat"
        self.draw(url)

    def draw(self, url):
        response = requests.get(url)
        bytes = io.BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(bytes.read())
        self.label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())