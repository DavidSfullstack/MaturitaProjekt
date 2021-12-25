import sys

from datetime import datetime
from bisect import bisect

from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QInputDialog, QHBoxLayout, QPushButton


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)

    def loginfunction(self):
        Login.user = self.name.text()
        Login.money = int(self.cash.text())
        if len(Login.user) == 0 or len(str(Login.money)) == 0 or any([char.isdigit() for char in Login.user]):
            self.errormsg.setText("Vyplňte platné údaje")
        else:
            self.gotomainscreen()
            self.createLists()

            cashamountstart = str(Login.money)
            today = datetime.today().strftime('%d-%m-%Y')
            logfile = open("záznam", "a")
            logfile.write(
                "\nDatum: " + today + "\nKasa začátek: " + cashamountstart + "Kč")
            logfile.close()

    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createLists(self):
        Login.availablelist = [1, 4, 6, 8, 11, 14]
        Login.currentlyrentedlist = []
        Login.toreturnlist = []


class MainScreen(QDialog):

    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("mainscreen.ui", self)
        timer = QTimer(self)
        timer.timeout.connect(self.displayTime)
        timer.timeout.connect(self.displayCashAmount)
        timer.start(1000)
        updatetimer = QTimer(self)
        updatetimer.setSingleShot(True)
        updatetimer.timeout.connect(self.updateavailable)
        updatetimer.start(1000)
        self.addbutton.clicked.connect(self.addCart)
        self.endbutton.clicked.connect(self.exitApp)
        self.available.setItemAlignment(QtCore.Qt.AlignCenter)
        self.removebutton.clicked.connect(self.removeCart)
        MainScreen.price = 30

    def displayCashAmount(self):
        self.cashamount.setText("Stav kasy: " + str(Login.money))

    def displayTime(self):
        currenttime = QTime.currentTime()
        displaytime = currenttime.toString('hh:mm:ss')
        self.timer.setAlignment(QtCore.Qt.AlignCenter)
        self.timer.setText(displaytime)

    def addCart(self):
        cartnum, ok = QInputDialog.getText(self, "Přidat motokáru", "Zadejte číslo motokáry")

        if ok:
            if int(cartnum) in Login.availablelist:
                print("Already exists")
            else:
                where = bisect(Login.availablelist, int(cartnum))
                Login.availablelist.insert(where, int(cartnum))
                self.updateavailable()

    def updateavailable(self):
        self.available.clear()
        for i in range(len(Login.availablelist)):

            cartwidget = QtWidgets.QListWidgetItem()

            customwidget = QtWidgets.QWidget()
            widgetButton = QtWidgets.QPushButton("Půjčit motokáru " + str(Login.availablelist[i]))
            widgetButton.setAccessibleName(str(Login.availablelist[i]))
            widgetButton.clicked.connect(self.borrowCart)
            widgetButton.setFixedWidth(375)
            widgetButton.setFixedHeight(41)
            widgetButton.setStyleSheet(
                "QPushButton"
                "{"
                "color: black;"
                "background-color: #DFF9FD;"
                "border-style: solid;"
                "border-width: 2px;"
                "border-color: #000000"
                "}"
                "QPushButton::hover"
                "{"
                "background-color : #B3BEFD;"
                "}"
            )
            widgetButton.setFont(QFont('Times', 15))

            customwidget.setStyleSheet(
                "color: black;"
                "background-color: #DFF9FD;"
                "border-style: solid;"
                "border-width: 3px;"
                "border-color: #000000"
            )
            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addStretch()
            widgetLayout.addWidget(widgetButton)
            widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            customwidget.setLayout(widgetLayout)
            cartwidget.setSizeHint(customwidget.sizeHint())

            self.available.insertItem(i, cartwidget)
            self.available.setItemWidget(cartwidget, customwidget)

    def borrowCart(self):
        Login.money = Login.money + 30

        timenow = datetime.now()
        timeofrent = (timenow.hour * 60) + timenow.minute

        buttonclicked = self.sender()
        rentedcart = int(buttonclicked.accessibleName())
        Login.currentlyrentedlist.append([rentedcart, timeofrent])
        Login.availablelist.remove(rentedcart)
        self.updaterented()
        self.updateavailable()


    def updaterented(self):
        self.currentlyrented.clear()
        for i in range(len(Login.currentlyrentedlist)):

            cartwidget = QtWidgets.QListWidgetItem()

            customwidget = QtWidgets.QWidget()
            widgetButton = QtWidgets.QPushButton("Půjčená motokára " + str(Login.currentlyrentedlist[i][0]))
            widgetButton.setAccessibleName(str(Login.currentlyrentedlist[i][0]))
            widgetButton.clicked.connect(self.borrowCart)
            widgetButton.setFixedWidth(375)
            widgetButton.setFixedHeight(41)
            widgetButton.setStyleSheet(
                "QPushButton"
                "{"
                "color: black;"
                "background-color: #c9e0fd;"
                "border-style: solid;"
                "border-width: 2px;"
                "border-color: #000000"
                "}"
                "QPushButton::hover"
                "{"
                "background-color : #B3BEFD;"
                "}"
            )
            widgetButton.setFont(QFont('Times', 15))

            customwidget.setStyleSheet(
                "color: black;"
                "background-color: #c9e0fd;"
                "border-style: solid;"
                "border-width: 3px;"
                "border-color: #000000"
            )
            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addStretch()
            widgetLayout.addWidget(widgetButton)
            widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            customwidget.setLayout(widgetLayout)
            cartwidget.setSizeHint(customwidget.sizeHint())

            self.currentlyrented.insertItem(i, cartwidget)
            self.currentlyrented.setItemWidget(cartwidget, customwidget)

    def removeCart(self):
        whichcart, ok = QInputDialog.getText(self, "Odebrat motokáru", "Zadejte číslo motokáry")
        if ok:
            self.available.takeItem(int(whichcart) - 1)

    # def markAsDefective:
    # def markAsUsable:

    def exitApp(self):

        cashamountend = str(Login.money)
        logfile = open("Záznam", "a")
        logfile.write(
            "\nKasa konec: " + cashamountend + "Kč\nJméno: " + Login.user + "\n ")
        logfile.close()

        app.quit()


# main
app = QApplication(sys.argv)
LoginScreen = Login()

widget = QStackedWidget()
widget.addWidget(LoginScreen)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
