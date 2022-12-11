import sys#библеотека отвечает за системные функции, кнопа , окно и тд
import math

from PyQt5 import uic  # Импортируем библиотеку uic, это наши интерфейсы 
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QSpinBox,QComboBox#импотируем все классы виджетов, виджеты это мой текст
import requests#импортирум библ для общения  с нашим сервер
import sqlite3

from PyQt5.uic.properties import QtCore

bd = sqlite3.connect('plants_bd.sqlite')#подкл нашу базу данных
cur = bd.cursor()#создаем курсор
res = cur.execute('''
SELECT id, title from plants
''').fetchall()# мы делаем запрос базу данных и берем все названия растения чтобы применить их в приложении
a = list(map(lambda x: x[1], res))#мы записавыем список с названиями растений

class Ui_MyDialog(QDialog):#создается класс диологового окна
    def __init__(self):#инициализируется
        super().__init__()#подтягиваются из род класса все функции
        uic.loadUi('2.ui', self)  # Загружаем дизайн
        self.pushButton.clicked.connect(self.run)# когда нажим кнопка выполняется функция селфран

    def run(self):# добавляем растение в базу данных
        if self.lineEdit.text() != "":#написанно ли название
            cur.execute(f'''
            INSERT INTO plants(title,pH,temprrature,vlagnost) VALUES("{self.lineEdit.text()}",{self.doubleSpinBox_2.value()},{self.spinBox.value()},{self.doubleSpinBox.value()})
            ''')#добавляем в базу данных в которую указвыем название и показатели посвы из указанных
            bd.commit()# применяем изменение которое внесли
            self.close()#закрываем окошко

class MyWidget(QMainWindow): # создаем класс
    def __init__(self):# создаем начальные параметры
        super().__init__()#подтягиваем все функции из род класса
        self.text = ''
        uic.loadUi('1.ui', self)  # Загружаем дизайн
        self.comboBox.insertItems(0, a)# присваиваем  названия наших растений
        self.pushButton.clicked.connect(self.run)#если нажали на кнопку покл функцию селфран
        self.pushButton_2.clicked.connect(self.add)

    def add(self): 
        dlg = Ui_MyDialog()
        dlg.exec()# инциализация нового  окна

        res = cur.execute('''
        SELECT id, title from plants
        ''').fetchall()#список новых названий получаем
        self.comboBox.clear()# очищаем наш выпадающий список
        a = list(map(lambda x: x[1], res))#весь список названий который в базе данных
        self.comboBox.insertItems(0, a)

    def run(self):
        self.jsonin = requests.get('http://172.20.10.3/helloWorld').json()#джейсон который получен с сервера
        print(self.jsonin)
        tm, vl = cur.execute(f'''
SELECT temprrature, vlagnost from plants
WHERE id = {self.comboBox.currentIndex() + 1}
''').fetchall()[0]# мы обращаемся к базе данных и получаем показатели почвы выбранного растения

        try:
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
        except Exception as d:
            print(d)#ловит ошибку




if __name__ == '__main__':# инициализация всего
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())



