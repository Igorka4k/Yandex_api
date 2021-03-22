import sys

from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import io


def find_place_address_and_index(place):
    response_address = requests.get("http://geocode-maps.yandex.ru/1.x/?"
                                    "apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                    f"geocode={place}&"
                                    "format=json").json()
    address = response_address['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
        'metaDataProperty']['GeocoderMetaData']['Address']['formatted']

    try:
        index = \
            response_address['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
    except KeyError:
        index = ''
    return address, index


class MyWidget(QMainWindow):
    point = False

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
        self.pushButton.clicked.connect(lambda: self.findPlace(self.lineEdit_4.text()))
        self.pushButton_2.clicked.connect(self.setView)
        self.pushButton_3.clicked.connect(self.clear_searching_row)
        self.checkBox.clicked.connect(lambda: self.findPlace(self.lineEdit_4.text()))
        self.fetchImage()

    def setView(self):
        self.view_index += 1
        self.view_index %= len(self.views)
        self.pushButton_2.setText(self.views[self.view_index][1])
        self.fetchImage()

    def clear_searching_row(self):
        self.point = False
        self.lineEdit_4.setText('')
        self.label_5.setText('')
        self.fetchImage()

    def findPlace(self, place):
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': place,
            'format': 'json',
        }
        response_address = requests.get("http://geocode-maps.yandex.ru/1.x/?",
                                        params).json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']

        self.lineEdit.setText(response_address.split()[0])
        self.lineEdit_2.setText(response_address.split()[1])
        address, index = find_place_address_and_index(place)
        if self.checkBox.isChecked() and index:
            self.label_5.setText(', '.join((address, index)))
        else:
            self.label_5.setText(address)
        self.fetchImage(True)

    def fetchImage(self, is_find=False):
        self.latitude = self.lineEdit.text()
        self.longitude = self.lineEdit_2.text()
        self.spn = self.lineEdit_3.text()
        static_url = "https://static-maps.yandex.ru/1.x/?"
        params = {
            "ll": f"{self.latitude},{self.longitude}",
            "spn": f"{self.spn},{self.spn}",
            "l": self.views[self.view_index][0]
        }
        if is_find:
            params["pt"] = f"{self.latitude},{self.longitude},flag"
            self.point = (self.latitude, self.longitude)
        if self.point:
            params["pt"] = f"{self.point[0]},{self.point[1]},flag"

        self.draw(static_url, params)

    def draw(self, url, params):
        response = requests.get(url, params)
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
            n = round(min(float(self.spn) + (float(self.spn) + 0.5) / 10, 90), 4)
            self.lineEdit_3.setText(str(n))
        if event.key() == Qt.Key_PageDown:
            n = round(max(float(self.spn) - (float(self.spn) + 0.5) / 10, 0.001), 4)
            self.lineEdit_3.setText(str(n))

        if event.key() == Qt.Key_W or event.key() == 1062:
            n = float(self.lineEdit_2.text()) + float(self.spn)
            if -90 <= n <= 90:
                self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_S or event.key() == 1067:
            n = float(self.lineEdit_2.text()) - float(self.spn)
            if -90 <= n <= 90:
                self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_A or event.key() == 1060:
            n = float(self.lineEdit.text()) - float(self.spn)
            if -180 <= n <= 180:
                self.lineEdit.setText(str(n))

        if event.key() == Qt.Key_D or event.key() == 1042:
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
