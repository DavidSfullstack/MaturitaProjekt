import sys

from datetime import date
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
        Login.money = self.cash.text()
        if len(Login.user) == 0 or len(Login.money) == 0 or any([char.isdigit() for char in Login.user]):
            self.errormsg.setText("Vyplňte platné údaje")
        else:
            self.gotomainscreen()
            self.createLists()

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
        self.addbutton.clicked.connect(self.addCart)
        self.endbutton.clicked.connect(self.exitApp)
        self.available.setItemAlignment(QtCore.Qt.AlignCenter)
        self.removebutton.clicked.connect(self.removeCart)
        # self.updateavailable()

    def displayCashAmount(self):
        MainScreen.currentcash = 7000
        self.cashamount.setText("Stav kasy: " + str(MainScreen.currentcash))

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
                Login.availablelist.insert(0, where)
                self.updateavailable()

    def updateavailable(self):
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
        self.available.takeItem(MainScreen.pos)

    def removeCart(self):
        whichcart, ok = QInputDialog.getText(self, "Odebrat motokáru", "Zadejte číslo motokáry")
        if ok:
            self.available.takeItem(int(whichcart) - 1)

    # def markAsDefective:
    # def markAsUsable:

    def exitApp(self):
        cashamountstart = str(Login.money)
        cashamountend = str(MainScreen.currentcash)
        today = str(date.today())
        logfile = open(today, "w+")
        logfile.write(
            "Datum: " + today + "\nKasa začátek: " + cashamountstart + "Kč" + "\nKasa konec: " + cashamountend + "Kč\nJméno: " + Login.user)
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
