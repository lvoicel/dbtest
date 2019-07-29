from io import BytesIO
import sqlite3
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
QDesktopWidget, QLabel, QLineEdit, QTextEdit, QGridLayout, QComboBox,
QFileDialog, QAction, QTableWidget, QTableWidgetItem, )
from PyQt5.QtGui import (QPixmap, QPainter, QImage, )
from datetime import datetime
import time
from PyQt5.QtCore import (Qt, QSize)

conn = sqlite3.connect("main.db")
cursor = conn.cursor()
print("Подключение к базе данных установлено")


cursor.execute("""CREATE TABLE IF NOT EXISTS base
                (name text, message text, time text,
                option text, image blob)
                """)
        
class DataB(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):

        author = QLabel('Ф.И.О.')
        message = QLabel('Сообщение')
        option = QLabel('Опция')


        self.authorEdit = QLineEdit(self)
        self.messageEdit = QTextEdit(self)
        fileDownload = QFileDialog()
        self.optionDDown = QComboBox()
        fileBtn = QPushButton('Загрузить файл')
        sendBtn = QPushButton('Отправить')
        thBtn = QPushButton('th')

        
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(author, 1, 0)
        grid.addWidget(self.authorEdit, 1, 1)

        grid.addWidget(message, 2, 0)
        grid.addWidget(self.messageEdit, 2, 1)

        grid.addWidget(fileBtn, 3, 1)
        fileBtn.clicked.connect(self.getFile)

        self.optionDDown.addItems(['По сайту', 'На форуме', 'Везде'])
        grid.addWidget(option, 4, 0)
        grid.addWidget(self.optionDDown, 4, 1)
        
        grid.addWidget(sendBtn, 5, 1)


        cursor.execute("""SELECT COUNT(*) FROM base""")
        rows = cursor.fetchone()
        print(rows)
        
        sendBtn.clicked.connect(self.sendRes)
        self.table = QTableWidget(self)
        self.table.setRowCount(rows[0])
        self.table.setColumnCount(7)
        grid.addWidget(self.table, 6, 0, 6, 4)
        edBtn = QPushButton('e')
        delBtn = QPushButton('d')



        cursor.execute("""SELECT * FROM base""")
        res = cursor.fetchall()
        i = 0
        j = 0

        if res:
            for i in range(rows[0]):
                #self.table.setCellWidget(0, 5, edBtn)
                #self.table.setCellWidget(0, 6, delBtn)
                for j in range(len(res[i])):
                    if (j == 4) & (res[i][j] != 0):
                        pic = BytesIO(res[i][j])
                        qimg = QImage.fromData(res[i][j])
                        pixmap = QPixmap()
                        pixmap.loadFromData(pic.getvalue())
                        image = QTableWidgetItem()
                        image.setData(Qt.DecorationRole, pixmap.scaled(50,50))
                        self.table.setItem(i, j, image)
                    else:
                        self.table.setItem(i, j, QTableWidgetItem(res[i][j]))
        


        self.setLayout(grid)
        self.resize(600, 500)
        self.setWindowTitle('Db')
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setMinimumSize(500,300)
        self.show()
        print("Оболочка успешно загружена")

    def sendRes(self):
        authorText = self.authorEdit.text()
        messageText = self.messageEdit.toPlainText()
        optionText = self.optionDDown.currentText()
        binary = sqlite3.Binary(self.img)
        print(binary)
        try:
            time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
            sql = ("INSERT INTO base (name, message, time, option, image) VALUES (?, ?, ?, ?, ?)")
            cursor.execute(sql, (authorText, messageText, time, optionText, binary))
            conn.commit()
            print("Данные отправлены")
        except:
            conn.rollback()
            print("Ошибка при отправке данных")

    def getFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                'c:\\',"Image files (*.jpg *.gif *.png *.bmp)")
        if fname:
            print(fname)
            filename = fname[0]
            try:
                fin = open(filename, "rb")
                print("Получаю файл...")
                self.img = fin.read()
                print(self.img)
            except:
                fin.close()
                print("Ошибка при чтении файла")
            finally:
                if fin:
                    fin.close()
                    fin = 0
        
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = DataB()
    sys.exit(app.exec_())
    conn.close()
    print("Подключение к базе данных закрыто")
