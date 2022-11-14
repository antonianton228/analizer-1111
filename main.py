import sys
import math

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
import requests
import sqlite3

from PyQt5.uic.properties import QtCore

bd = sqlite3.connect('plants_bd.sqlite')
cur = bd.cursor()
res = cur.execute('''
SELECT id, title from plants
''').fetchall()
print(res)
a = list(map(lambda x: x[1], res))

class Ui_MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('2.ui', self)  # Загружаем дизайн
        self.pushButton.clicked.connect(self.run)

    def run(self):
        pass

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text = ''
        uic.loadUi('1.ui', self)  # Загружаем дизайн
        self.comboBox.insertItems(0, a)
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.add)

    def add(self):
        dlg = Ui_MyDialog()
        dlg.exec()

    def run(self):
        self.jsonin = requests.get('http://172.20.10.3/helloWorld').json()
        print(self.jsonin)
        tm, vl = cur.execute(f'''
SELECT temprrature, vlagnost from plants
WHERE id = {self.comboBox.currentIndex() + 1}
''').fetchall()[0]


        self.text = ''
        if int(self.jsonin["Humidity"]) - 50 > vl:
            self.text += f'слишком влажно, осушите на {round(((int(self.jsonin["Humidity"]) - vl) / 1023)*100, 2)}%'
        elif int(self.jsonin["Humidity"]) + 50 < vl:
            self.text += f'слишком сухо, увлажните на {round(((vl - int(self.jsonin["Humidity"])) / 1023) * 100, 2)}%'
        else:
            self.text += "Влажность в норме"

        self.text += '\n'
        if float(self.jsonin["Temperature"]) - 2.5 > tm:
            self.text += f'слишком тепло, остудите на {round((float(self.jsonin["Temperature"]) - tm) , 2)}%'
        elif float(self.jsonin["Temperature"]) + 2.5 < tm:
            self.text += f'слишком холодно, увеличте на {round((tm - float(self.jsonin["Temperature"])) , 2)}%'
        else:
            self.text += "Температура в норме"

        self.textEdit.setText(self.text)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())



