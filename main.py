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
        self.views = [('map', 'Схема'), ('sat', 'Спутник'), ('sat,skl', 'Гибрид')]
        self.view_index = 0
        self.lineEdit.setText("35.35")
        self.lineEdit_2.setText("35.35")
        self.spn = self.lineEdit_3.setText('1.0')
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.fetchImage)
        self.pushButton_2.clicked.connect(self.setView)
        self.fetchImage()

    def setView(self):
        self.view_index += 1
        self.view_index %= len(self.views)
        self.pushButton_2.setText(self.views[self.view_index][1])
        self.fetchImage()

    def fetchImage(self):
        self.latitude = self.lineEdit.text()
        self.longitude = self.lineEdit_2.text()
        self.spn = self.lineEdit_3.text()
        self.url = f"https://static-maps.yandex.ru/1.x/?ll={self.latitude},{self.longitude}&spn={self.spn},{self.spn}&l={self.views[self.view_index][0]}"
        self.draw(self.url)

    def draw(self, url):
        self.response = requests.get(url)
        bytes = io.BytesIO(self.response.content)
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
            n = round(min(float(self.spn) + (float(self.spn) + 0.5) / 10, 90), 4)
            self.lineEdit_3.setText(str(n))
        if event.key() == Qt.Key_PageDown:
            n = round(max(float(self.spn) - (float(self.spn) + 0.5) / 10, 0.001), 4)
            self.lineEdit_3.setText(str(n))

        if event.key() == Qt.Key_W:
            n = float(self.lineEdit_2.text()) + float(self.spn)
            if -90 <= n <= 90:
                self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_S:
            n = float(self.lineEdit_2.text()) - float(self.spn)
            if -90 <= n <= 90:
                self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_A:
            n = float(self.lineEdit.text()) - float(self.spn)
            if -180 <= n <= 180:
                self.lineEdit.setText(str(n))

        if event.key() == Qt.Key_D:
            n = float(self.lineEdit.text()) + float(self.spn)
            if -180 <= n <= 180:
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
