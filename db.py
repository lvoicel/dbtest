from io import BytesIO
import sqlite3
import sys
from PyQt5.Qt import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QLineEdit, QTextEdit, QGridLayout, QComboBox,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime

conn = sqlite3.connect("main.db")
cursor = conn.cursor()
print("Подключение к базе данных установлено")
global idR
idR = 0
cursor.execute("""CREATE TABLE IF NOT EXISTS base
                (num int, name text, message text, time text,
                option text, image blob)
                """)

cursor.execute("""CREATE TABLE IF NOT EXISTS users
                (num int, name text, surname text, middlename text,
                usergroup text, login text, pass text)
                """)


class DataB(QWidget):

    def __init__(self, userGroup):
        super(DataB, self).__init__()
        self.initUI(userGroup)

    def initUI(self, userGroup):
        self.userGroup = userGroup
        self.author = QLabel('Ф.И.О.')
        self.message = QLabel('Сообщение')
        self.option = QLabel('Опция')
        self.timeL = QLabel('Время заявки')
        self.imageL = QLabel('Изображение')
        self.authorEdit = QLineEdit(self)
        self.authorEdit.setMaximumSize(340, 30)
        self.messageEdit = QTextEdit(self)
        self.messageEdit.setMaximumSize(340, 90)
        self.optionDDown = QComboBox()
        fileBtn = QPushButton('Обзор...')
        sendBtn = QPushButton('Отправить')
        delBtn = QPushButton('Удалить строку')
        self.fnameEdit = QLineEdit(self)
        self.fnameEdit.setReadOnly(1)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(self.author, 1, 0)
        grid.addWidget(self.authorEdit, 1, 1, 1, 4)
        grid.addWidget(self.message, 2, 0)
        grid.addWidget(self.messageEdit, 2, 1, 1, 4)
        grid.addWidget(self.fnameEdit, 3, 1, 1, 3)
        grid.addWidget(fileBtn, 3, 4)
        fileBtn.clicked.connect(self.getFile)
        self.optionDDown.addItems(['По сайту', 'На форуме', 'Везде'])
        grid.addWidget(self.option, 4, 0)
        grid.addWidget(self.optionDDown, 4, 1, 1, 2)
        grid.addWidget(sendBtn, 4, 3, 1, 2)
        sendBtn.clicked.connect(self.sendRes)
        grid.addWidget(delBtn, 4, 6, 1, 2)
        delBtn.clicked.connect(self.delRow)
        delBtn.setMaximumSize(120, 30)
        self.img = 0
        self.table = QTableWidget(self)
        grid.addWidget(self.table, 5, 0, 7, 8)
        self.getBase()
        self.setLayout(grid)
        self.resize(700, 500)
        self.setWindowTitle('Db')
        self.table.setSortingEnabled(1)
        self.table.setMinimumSize(500, 300)
        print("Оболочка успешно загружена")

    def getBase(self):
        cursor.execute("SELECT COUNT(*) FROM base")
        self.rows = cursor.fetchone()
        self.table.setRowCount(self.rows[0])
        self.table.setColumnCount(6)
        labels = (
            "№", "Ф.И.О.", "Сообщение", "Время заявки", "Опция", "Изображение")
        self.table.setHorizontalHeaderLabels(labels)
        cursor.execute("SELECT * FROM base")
        res = cursor.fetchall()
        i = 0
        j = 0
        if res:
            for i in range(self.rows[0]):
                for j in range(len(res[i])):
                    if j == 0:
                        item = QTableWidgetItem(str(res[i][j]))
                        if self.userGroup == ("guest" or "user"):
                            item.setFlags(Qt.ItemIsEditable)
                        self.table.setItem(i, j, item)
                    elif (j == 5) & (res[i][j] != 0):
                        pic = BytesIO(res[i][j])
                        pixmap = QPixmap()
                        pixmap.loadFromData(pic.getvalue())
                        image = QTableWidgetItem()
                        image.setData(
                            Qt.DecorationRole, pixmap.scaled(
                                80, 80, Qt.KeepAspectRatio))
                        self.table.setItem(i, j, image)
                    else:
                        item = QTableWidgetItem(res[i][j])
                        if self.userGroup == ("guest" or "user"):
                            item.setFlags(Qt.ItemIsEditable)
                        self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch)
        self.table.resizeRowsToContents()

    def delRow(self):
        curr = self.table.currentRow()
        currow = self.table.item(curr, 0).text()
        cursor.execute("DELETE FROM base WHERE num = ?", (currow, ))
        conn.commit()
        self.table.removeRow(curr)

    def sendRes(self):
        cursor.execute("SELECT MAX(`num`) FROM base")
        curid = cursor.fetchone()[0]
        if curid is None:
            idR = 1
        else:
            idR = curid + 1
        authorText = self.authorEdit.text()
        messageText = self.messageEdit.toPlainText()
        optionText = self.optionDDown.currentText()
        if self.img:
            binary = sqlite3.Binary(self.img)
        else:
            binary = 0
        try:
            time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
            sql = (
                """INSERT INTO base (num, name, message, time, option, image)
                VALUES (?, ?, ?, ?, ?, ?)""")
            cursor.execute(sql, (
                idR, authorText, messageText, time, optionText, binary))
            conn.commit()
            print("Данные отправлены")
        except ConnectionError:
            conn.rollback()
            print("Ошибка при отправке данных")
        self.getBase()

    def getFile(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', 'c:\\', "Image files (*.jpg *.gif *.png *.bmp)")
        if fname:
            filename = fname[0]
            self.fnameEdit.setText(fname[0])
            try:
                fin = open(filename, "rb")
                print("Получаю файл...")
                self.img = fin.read()
            except OSError:
                print("Ошибка при чтении файла")
            finally:
                try:
                    fin.close()
                    fin = 0
                except UnboundLocalError:
                    print("Файл не выбран")


class Auth(QWidget):

    def __init__(self):
        super(Auth, self).__init__()
        self.setWindowTitle('Авторизация')
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(400, 200)
        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.login = QLineEdit("Логин")
        self.login.setMaximumWidth(200)
        self.password = QLineEdit("Пароль")
        self.password.setMaximumWidth(200)
        self.authBtn = QPushButton('Войти')
        grid.setSpacing(2)
        grid.addWidget(self.msg, 1, 1, 1, 3)
        grid.addWidget(self.login, 2, 1)
        grid.addWidget(self.password, 2, 3)
        grid.addWidget(self.authBtn, 3, 1, 3, 3)
        self.authBtn.clicked.connect(self.authorize)

    def authorize(self):
        user = self.login.text()
        password = self.password.text()
        cursor.execute("SELECT pass FROM users WHERE login = ?", (str(user), ))
        result = cursor.fetchone()
        if (result[0]) and (result[0] == str(password)):
            cursor.execute(
                "SELECT usergroup FROM users WHERE login = ?", (str(user), ))
            authorized = cursor.fetchone()[0]
            self.showDataB(authorized)
        if (result[0]) is None or (result[0] != str(password)):
            self.msg.setText("""<h1 style="color: rgb(250, 55, 55);">
                Неверная пара логин|пароль</h1>""")
            self.msg.setFont(QFont("Arial", 8, QFont.Bold))

    def showDataB(self, authorized):
        self.db = DataB(str(authorized))
        self.db.show()
        self.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    auth = Auth()
    auth.show()
    sys.exit(app.exec_())
    conn.close()
    print("Подключение к базе данных закрыто")
