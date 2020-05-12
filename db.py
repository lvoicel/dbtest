from io import BytesIO
import sqlite3
import sys
from PyQt5.Qt import (QFont)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QLineEdit, QTextEdit, QGridLayout, QComboBox,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import (QPixmap, QRegExpValidator)
from PyQt5.QtCore import (Qt, QRegExp)
from datetime import (datetime)

conn = sqlite3.connect("main.db")
# Connecting to db
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
                usergroup text, login text, pass text, tel text, email text)
                """)


class DataB(QWidget):
    # Main Window

    def __init__(self):
        super(DataB, self).__init__()
        self.initUI()

    def initUI(self):
        user = CurUser
        # Design of main window
        self.userGroup = user.userGroup
        self.author = QLabel('Ф.И.О.')
        self.message = QLabel('Сообщение')
        self.option = QLabel('Опция')
        self.timeL = QLabel('Время заявки')
        self.imageL = QLabel('Изображение')
        self.authorEdit = QLineEdit(self)
        self.authorEdit.setMaximumHeight(30)
        fio = (user.surName + " " + user.name[0] + ". "
                            + user.middleName[0] + ".")
        if self.userGroup == ("guest" or "user"):
            self.authorEdit.setReadOnly(1)
        self.authorEdit.setText(fio)
        self.setWindowTitle('DB - ' + fio)
        self.messageEdit = QTextEdit(self)
        self.authorEdit.setMaximumHeight(90)
        self.status = QComboBox()
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
        self.status.addItems(['Принята', 'Дизайн', 'В работу',
                              'Выполняется', 'Готова', 'Закрыта',
                              'Отложена'])
        grid.addWidget(self.option, 4, 0)
        grid.addWidget(self.status, 4, 1, 1, 2)
        grid.addWidget(sendBtn, 4, 3, 1, 2)
        sendBtn.clicked.connect(self.sendRes)
        reloadBtn = QPushButton("Обновить")
        grid.addWidget(reloadBtn, 4, 5)
        grid.addWidget(delBtn, 4, 6)
        reloadBtn.clicked.connect(self.getBase)
        delBtn.clicked.connect(self.delRow)
        delBtn.setMaximumSize(120, 30)
        self.img = 0
        self.table = QTableWidget(self)
        self.table.setSortingEnabled(1)
        grid.addWidget(self.table, 5, 0, 7, 7)
        if self.userGroup == ("admin" or "user"):
            self.getBase()
        self.setLayout(grid)
        self.resize(700, 500)
        self.table.setMinimumSize(500, 300)
        print("Оболочка успешно загружена")

    def getBase(self):
        # Creating a QTableWidget
        # curOrder = Order()
        cursor.execute("SELECT COUNT(*) FROM base")
        self.table.sortByColumn(0, Qt.SortOrder(0))
        self.table.setRowCount(0)
        self.rows = cursor.fetchone()
        self.table.setRowCount(self.rows[0])
        self.table.setColumnCount(6)
        labels = (
            "№", "Ф.И.О.", "Комментарии", "Время заявки",
            "Опция", "Изображение")
        self.table.setHorizontalHeaderLabels(labels)
        cursor.execute("SELECT * FROM base")

        res = cursor.fetchall()
        i = 0
        j = 0
        # Adding content in QTable
        if res:
            for i in range(self.rows[0]):
                for j in range(len(res[i])):
                    if j == 0:
                        item = QTableWidgetItem(str(res[i][j]))
                        # User group check for permissions
                        if self.userGroup == ("guest" or "user"):
                            item.setFlags(Qt.ItemIsEditable)
                        self.table.setItem(i, j, item)
                    # Adding an image from db in QTable
                    elif (j == 5) & (res[i][j] != 0):
                        pic = BytesIO(res[i][j])
                        pixmap = QPixmap()
                        pixmap.loadFromData(pic.getvalue())
                        image = QTableWidgetItem()
                        image.setData(
                            Qt.DecorationRole, pixmap.scaled(
                                80, 80, Qt.KeepAspectRatio))
                        self.table.setItem(i, j, image)
                    elif (j == 3):
                        item = QTableWidgetItem(res[i][j])
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(i, j, item)
                    else:
                        item = QTableWidgetItem(res[i][j])
                        if self.userGroup == ("guest" or "user"):
                            item.setFlags(Qt.ItemIsEditable)
                        self.table.setItem(i, j, item)

        self.table.verticalHeader().hide()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(1, 110)
        self.table.resizeRowsToContents()
        self.table.sortByColumn(0, Qt.SortOrder(1))

    def delRow(self):
        # Deliting selected row from QTable and db function
        curr = self.table.currentRow()
        if self.table.item(curr, 0) is None:
            print("Строка не выбрана")
        else:
            currow = self.table.item(curr, 0).text()
            cursor.execute("DELETE FROM base WHERE num = ?", (currow, ))
            conn.commit()
            self.getBase()

    def sendRes(self):
        # Sending data in db function
        cursor.execute("SELECT MAX(`num`) FROM base")
        curid = cursor.fetchone()[0]
        if curid is None:
            idR = 1
        else:
            idR = curid + 1
        authorText = self.authorEdit.text()
        messageText = self.messageEdit.toPlainText()
        optionText = self.status.currentText()
        if self.img:
            # Image blob
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
            self.fnameEdit.setText("")
            self.messageEdit.setText("")
        except ConnectionError:
            conn.rollback()
            print("Ошибка при отправке данных")
        if self.userGroup == ("admin" or "user"):
            self.getBase()

    def getFile(self):
        # Selecting an image for sending in db
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', "./", "Image files (*.jpg *.gif *.png *.bmp)")
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


class Order(object):
    def __init__(self):
        super(Order, self).__init__()
    num = 0
    client = ""
    name = ""
    typeOfWorks = ()
    status = ""
    price = ''
    startDate = ''
    endDate = ''
    manager = ''
    filesPath = ''
    preview = ''
    lastModified = ''
    material = ()
    implementer = ()
    isOver = bool


class CurUser(object):
    def __init__(self):
        super(CurUser, self).__init__()


class Auth(QWidget):
    # Authentication window

    def __init__(self):
        super(Auth, self).__init__()
        # Design of authentication window
        self.setWindowTitle('Авторизация')
        validator = QRegExp("[А-Яа-яA-Za-z0-9-_]+")
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(400, 200)
        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setMaximumSize(400, 30)
        self.login = QLineEdit("Логин")
        self.login.setMaximumWidth(200)
        self.login.setValidator(QRegExpValidator(validator))
        self.login.setMaxLength(10)
        self.password = QLineEdit("Пароль")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMaximumWidth(200)
        self.password.setValidator(QRegExpValidator(validator))
        self.password.setMaxLength(10)
        self.password.returnPressed.connect(self.authorize)
        self.login.returnPressed.connect(self.authorize)
        self.authBtn = QPushButton('Войти')
        self.authBtn.setMaximumSize(200, 50)
        self.regBtn = QPushButton('Регистрация')
        self.regBtn.setMaximumSize(200, 30)
        grid.setSpacing(2)
        grid.addWidget(self.msg, 1, 1, 1, 3)
        grid.addWidget(self.login, 2, 2)
        grid.addWidget(self.password, 3, 2)
        grid.addWidget(self.authBtn, 4, 2)
        grid.addWidget(self.regBtn, 5, 2)
        self.authBtn.clicked.connect(self.authorize)
        self.regBtn.clicked.connect(self.register)

    def authorize(self):
        # Creating "User" object from db to log in
        login = self.login.text()
        password = self.password.text()
        cursor.execute(
            "SELECT pass FROM users WHERE login = ?", (str(login), ))
        result = cursor.fetchone()
        if result is None:
            self.msg.setText("""<h1 style="color: rgb(250, 55, 55);">
                Неверная пара логин|пароль</h1>""")
            self.msg.setFont(QFont("Arial Bold", 6, QFont.Bold))
        elif (result[0] != str(password)):
            self.msg.setText("""<h1 style="color: rgb(250, 55, 55);">
                Неверная пара логин|пароль</h1>""")
            self.msg.setFont(QFont("Arial Bold", 6, QFont.Bold))
        elif result[0] == str(password):
            cursor.execute(
                "SELECT * FROM users WHERE login = ?", (str(login), ))
            result = cursor.fetchone()
            CurUser.num = result[0]
            CurUser.name = result[1]
            CurUser.surName = result[2]
            CurUser.middleName = result[3]
            CurUser.userGroup = result[4]
            CurUser.login = result[5]
            CurUser.password = result[6]
            self.showDataB()

    def showDataB(self):
        self.db = DataB()
        self.db.show()
        self.close()

    def register(self):
        self.reg = Register()
        self.reg.show()
        self.close()


class Register(QWidget):

    def __init__(self):
        super(Register, self).__init__()
        # Design of registration window
        self.setWindowTitle('Регистрация')
        validator = QRegExp("[А-Яа-яA-Za-z0-9-_]+")
        val2 = QRegExp("[А-яа-я]+")
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 240)
        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setMaximumSize(400, 30)
        self.msg.setFont(QFont("Arial Bold", 6, QFont.Bold))
        self.name = QLineEdit("Имя")
        self.name.setMaximumWidth(200)
        self.name.setValidator(QRegExpValidator(val2))
        self.middleName = QLineEdit("Отчество")
        self.middleName.setMaximumWidth(200)
        self.middleName.setValidator(QRegExpValidator(validator))
        self.surName = QLineEdit("Фамилия")
        self.surName.setMaximumWidth(200)
        self.surName.setValidator(QRegExpValidator(validator))
        self.login = QLineEdit("Логин")
        self.login.setMaximumWidth(200)
        self.login.setValidator(QRegExpValidator(validator))
        self.login.setMaxLength(10)
        self.password = QLineEdit("Пароль")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMaximumWidth(200)
        self.password.setValidator(QRegExpValidator(validator))
        self.password.setMaxLength(10)
        self.password.returnPressed.connect(self.push)
        self.password2 = QLineEdit("Пароль")
        self.password2.setEchoMode(QLineEdit.Password)
        self.password2.setMaximumWidth(200)
        self.password2.setValidator(QRegExpValidator(validator))
        self.password2.setMaxLength(10)
        self.password2.returnPressed.connect(self.push)
        self.login.returnPressed.connect(self.push)
        self.regBtn = QPushButton('Зарегистрироваться')
        self.regBtn.setMaximumSize(200, 50)
        self.backBtn = QPushButton('Назад')
        self.backBtn.setMaximumSize(50, 50)
        grid.setSpacing(5)
        grid.addWidget(self.msg, 1, 1, 1, 5)
        grid.addWidget(self.name, 2, 2, 1, 3)
        grid.addWidget(self.middleName, 3, 2, 1, 3)
        grid.addWidget(self.surName, 4, 2, 1, 3)
        grid.addWidget(self.login, 5, 2, 1, 3)
        grid.addWidget(self.password, 6, 2, 1, 3)
        grid.addWidget(self.password2, 7, 2, 1, 3)
        grid.addWidget(self.regBtn, 8, 3, 1, 2)
        grid.addWidget(self.backBtn, 8, 2)
        self.regBtn.clicked.connect(self.push)
        self.backBtn.clicked.connect(self.ok)

    def push(self):
        cursor.execute("SELECT MAX(`num`) FROM users")
        lastId = cursor.fetchone()[0]
        userGroup = 'user'
        if lastId is None:
            idU = 1
        else:
            idU = lastId + 1
        cursor.execute("SELECT * FROM users WHERE login = ?",
                       (self.login.text(), ))
        res = cursor.fetchone()
        if res is None:
            sql = ("""INSERT INTO users (num, name, surname, middlename, usergroup, login, pass)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""")
            cursor.execute(sql, (int(idU), self.name.text(),
                                 self.surName.text(),
                                 self.middleName.text(), userGroup,
                                 self.login.text(), self.password.text()))
            conn.commit()
            self.ok()
        elif self.password.text() != self.password2.text():
            self.msg.setText("""<h1 style="color: rgb(250, 55, 55);">
                Пароли не совпадают</h1>""")
        else:
            self.msg.setText("""<h1 style="color: rgb(250, 55, 55);">
                Логин уже используется</h1>""")

    def ok(self):
        self.auth = Auth()
        self.auth.show()
        self.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    auth = Auth()
    auth.show()
    sys.exit(app.exec_())
    conn.close()
    print("Подключение к базе данных закрыто")
