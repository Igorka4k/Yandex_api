import sys

from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtCore import Qt
import requests
import io
import math


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
        self.markerLat = '0.0'
        self.markerLong = '0.0'
        self.isMarkerSet = False
        self.views = [('map', 'Схема'), ('sat', 'Спутник'), ('sat,skl', 'Гибрид')]
        self.view_index = 0
        self.lineEdit.setText("35.35")
        self.lineEdit_2.setText("35.35")
        self.z = self.lineEdit_3.setText('4')
        self.zarr = [80]
        for i in range(1, 17):
            self.zarr.append(self.zarr[i - 1] / 2)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(lambda: self.findPlace(self.lineEdit_4.text()))
        self.pushButton_2.clicked.connect(self.setView)
        self.pushButton_3.clicked.connect(self.clear_searching_row)
        self.checkBox.clicked.connect(lambda: self.findPlace(self.lineEdit_4.text(), True))
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

    def findPlace(self, place, postalChange=False):
        if postalChange and self.isMarkerSet:
            self.findByCoord((self.markerLong, self.markerLat))
            return
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': place,
            'format': 'json',
        }
        response_address = requests.get("http://geocode-maps.yandex.ru/1.x/?",
                                        params).json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        if not postalChange:
            self.isMarkerSet = False
            self.lineEdit_2.setText(response_address.split()[0])
            self.lineEdit.setText(response_address.split()[1])
        address, index = find_place_address_and_index(place)
        if self.checkBox.isChecked() and index:
            self.label_5.setText(', '.join((address, index)))
        else:
            self.label_5.setText(address)
        if not postalChange:
            self.fetchImage(True)

    def findByCoord(self, coord, doReturn=False):
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': f"{coord[0]},{coord[1]}",
            'format': 'json',
        }
        response_address = requests.get("http://geocode-maps.yandex.ru/1.x/?",
                                        params).json()
        address = response_address['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        if doReturn:
            return address
        try:
            postal_code = response_address['response']['GeoObjectCollection'][
                'featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        except KeyError:
            postal_code = None
        if self.checkBox.isChecked() and postal_code:
            self.label_5.setText(', '.join((address, postal_code)))
        else:
            self.label_5.setText(address)

    def findOrganisationByCoord(self, coord, text):
        params = {
            "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
            'text': text,
            'lang': 'ru_RU',
            'spn': f"0.002,{abs(0.002 * math.cos(coord[1]))}",
            'll': f"{coord[0]},{coord[1]}",
            'rspn': 1,
            'format': 'json',
            'type': 'biz',
            'results': 1
        }
        response = requests.get("https://search-maps.yandex.ru/v1/", params)
        print(response.url)
        jsonobj = response.json()
        coord = jsonobj['features'][0]['geometry']['coordinates']
        self.setPoint((coord[0], coord[1]))
        name = jsonobj['features'][0]['properties']['name']
        self.label_5.setText(name)

    def setPoint(self, coord):
        self.isMarkerSet = True
        self.markerLong = coord[0]
        self.markerLat = coord[1]
        self.fetchImage(is_point=True, pointCoord=coord)

    def fetchImage(self, is_find=False, is_point=False, pointCoord=0):
        self.latitude = self.lineEdit.text()
        self.longitude = self.lineEdit_2.text()
        self.z = self.lineEdit_3.text()
        static_url = "https://static-maps.yandex.ru/1.x/?"
        params = {
            "ll": f"{self.longitude},{self.latitude}",
            "z": str(self.z),
            "l": self.views[self.view_index][0]
        }
        if is_find:
            # params["pt"] = f"{self.latitude},{self.longitude},flag"
            self.point = (self.longitude, self.latitude)
        if is_point:
            # params["pt"] = f"{pointCoord[0]},{pointCoord[1]},flag"=
            self.point = (pointCoord[0], pointCoord[1])
        if self.point:
            params["pt"] = f"{self.point[0]},{self.point[1]},flag"
        print(params)
        self.draw(static_url, params)

    def draw(self, url, params):
        response = requests.get(url, params)
        bytes = io.BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(bytes.read())
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        try:
            int(self.z)
        except Exception:
            self.z = 2
        try:
            float(self.lineEdit.text())
        except Exception:
            self.lineEdit.setText('35.35')
        try:
            float(self.lineEdit.text())
        except Exception:
            self.lineEdit.setText("35.35")
        if event.key() == Qt.Key_PageUp:
            self.lineEdit_3.setText(str(int(self.z) + 1))
        if event.key() == Qt.Key_PageDown:
            self.lineEdit_3.setText(str(int(self.z) - 1))

        if event.key() == Qt.Key_W or event.key() == 1062:
            n = float(self.lineEdit.text()) + self.zarr[int(self.z) - 1]
            if -90 <= n <= 90:
                self.lineEdit.setText(str(n))

        if event.key() == Qt.Key_S or event.key() == 1067:
            n = float(self.lineEdit.text()) - self.zarr[int(self.z) - 1]
            if -90 <= n <= 90:
                self.lineEdit.setText(str(n))

        if event.key() == Qt.Key_A or event.key() == 1060:
            n = float(self.lineEdit_2.text()) - self.zarr[int(self.z) - 1]
            if -180 <= n <= 180:
                self.lineEdit_2.setText(str(n))

        if event.key() == Qt.Key_D or event.key() == 1042:
            n = float(self.lineEdit_2.text()) + self.zarr[int(self.z) - 1]
            if -180 <= n <= 180:
                self.lineEdit_2.setText(str(n))
        self.fetchImage()

    def mousePressEvent(self, event):
        x = event.pos().x() - 10
        y = event.pos().y() - 170
        if x >= 0 and y >= 0 and x <= 600 and y <= 450:
            if int(self.z) <= 3:
                return
            xpart = x / 600
            ypart = y / 450
            latdif = 285 / (2 ** (int(self.z)))
            longdif = 420 / (2 ** (int(self.z)))
            newlong = float(self.longitude) - longdif + (longdif * 2) * xpart
            newlat = float(self.latitude) + latdif - (latdif * 2) * ypart
            a = math.cos(math.radians(float(self.latitude)))
            b = newlat - float(self.latitude)
            c = a * b
            if float(self.latitude) > 0:
                if b > 0:
                    # b = math.cos(float(self.latitude)) * (newlat - float(self.latitude))
                    # print(b)
                    newlat = float(self.latitude) + c
                else:
                    newlat = float(self.latitude) + c * 1.25
            else:
                if b > 0:
                    newlat = float(self.latitude) + c * 1.25
                else:
                    newlat = float(self.latitude) + c
            if event.buttons() == Qt.LeftButton:
                self.setPoint((newlong, newlat))  # long, lat (долгота, широта)
                self.findByCoord((newlong, newlat))
            elif event.buttons() == Qt.RightButton:
                self.findOrganisationByCoord((newlong, newlat), self.findByCoord((newlong, newlat), True))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
