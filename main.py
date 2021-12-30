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
        Login.availablelist = [[1, 0], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1]]
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
        updatetimer.timeout.connect(self.updateAvailable)
        updatetimer.start(1000)

        returntimer = QTimer(self)
        returntimer.timeout.connect(self.checkIfToReturn)
        returntimer.start(1000)

        self.addbutton.clicked.connect(self.addCart)
        self.endbutton.clicked.connect(self.exitApp)
        self.available.setItemAlignment(QtCore.Qt.AlignCenter)
        self.removebutton.clicked.connect(self.removeCart)
        self.defectivebutton.clicked.connect(self.markAsDefective)
        self.fixedbutton.clicked.connect(self.markAsUsable)

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
                self.updateAvailable()

    def updateAvailable(self):
        self.available.clear()
        for i in range(len(Login.availablelist)):
            if Login.availablelist[i][1] == 1:
                cartwidget = QtWidgets.QListWidgetItem()

                customwidget = QtWidgets.QWidget()
                widgetButton = QtWidgets.QPushButton("Půjčit motokáru " + str(Login.availablelist[i][0]))
                widgetButton.setAccessibleName(str(Login.availablelist[i][0]))
                widgetButton.clicked.connect(self.borrowCart)
                widgetButton.setFixedWidth(355)
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
                    "background-color : #c9e0fd;"
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

            else:
                cartwidget = QtWidgets.QListWidgetItem()

                customwidget = QtWidgets.QWidget()
                widgetText = QtWidgets.QLabel("Nefunkční motokára " + str(Login.availablelist[i][0]))
                widgetText.setFixedWidth(355)
                widgetText.setFixedHeight(41)
                widgetText.setStyleSheet(
                    "QLabel"
                    "{"
                    "color: black;"
                    "background-color: #ffd2aa;"
                    "border-style: solid;"
                    "border-width: 2px;"
                    "border-color: #000000"
                    "}"
                )
                widgetText.setFont(QFont('Times', 15))
                widgetText.setAlignment(QtCore.Qt.AlignCenter)

                customwidget.setStyleSheet(
                    "color: black;"
                    "background-color: #ffd2aa;"
                    "border-style: solid;"
                    "border-width: 3px;"
                    "border-color: #000000"
                )
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addStretch()
                widgetLayout.addWidget(widgetText)
                widgetLayout.addStretch()

                widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
                customwidget.setLayout(widgetLayout)
                cartwidget.setSizeHint(customwidget.sizeHint())

                self.available.insertItem(i, cartwidget)
                self.available.setItemWidget(cartwidget, customwidget)

    def borrowCart(self):
        Login.money = Login.money + 30

        timenow = datetime.now()
        timetoreturn = (timenow.hour * 60) + timenow.minute + 1

        rentclicked = self.sender()
        rentedcart = int(rentclicked.accessibleName())
        Login.currentlyrentedlist.append([rentedcart, timetoreturn])

        templist = [i[0] for i in Login.availablelist]
        indextorent = templist.index(rentedcart)
        del Login.availablelist[indextorent]

        self.updateRented()
        self.updateAvailable()
        self.displayCashAmount()

    def updateRented(self):
        self.currentlyrented.clear()
        for i in range(len(Login.currentlyrentedlist)):
            cartwidget = QtWidgets.QListWidgetItem()

            customwidget = QtWidgets.QWidget()
            widgetButton = QtWidgets.QPushButton("Zrušit číslo " + str(Login.currentlyrentedlist[i][0]))
            widgetButton.setAccessibleName(str(Login.currentlyrentedlist[i][0]))
            widgetButton.clicked.connect(self.cancelRent)
            widgetButton.setFixedWidth(173)
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

            widgetButton2 = QtWidgets.QPushButton("Vrátit číslo " + str(Login.currentlyrentedlist[i][0]))
            widgetButton2.setAccessibleName(str(Login.currentlyrentedlist[i][0]))
            widgetButton2.clicked.connect(self.returnEarly)
            widgetButton2.setFixedWidth(173)
            widgetButton2.setFixedHeight(41)
            widgetButton2.setStyleSheet(
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
            widgetButton2.setFont(QFont('Times', 15))
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
            widgetLayout.addWidget(widgetButton2)
            widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            customwidget.setLayout(widgetLayout)
            cartwidget.setSizeHint(customwidget.sizeHint())

            self.currentlyrented.insertItem(i, cartwidget)
            self.currentlyrented.setItemWidget(cartwidget, customwidget)

    def cancelRent(self):
        Login.money = Login.money - 30
        self.displayCashAmount()

        cancelclicked = self.sender()
        cancelledcart = int(cancelclicked.accessibleName())

        templist = [i[0] for i in Login.availablelist]
        whereto = bisect(templist, cancelledcart)
        Login.availablelist.insert(whereto, [cancelledcart, 1])

        templist2 = [i[0] for i in Login.currentlyrentedlist]
        indextocancel2 = templist2.index(cancelledcart)
        del Login.currentlyrentedlist[indextocancel2]

        self.updateRented()
        self.updateAvailable()

    def returnEarly(self):
        returnclicked = self.sender()
        returnedcart = int(returnclicked.accessibleName())

        templist = [i[0] for i in Login.availablelist]
        whereto = bisect(templist, returnedcart)
        Login.availablelist.insert(whereto, [returnedcart, 1])

        templist2 = [i[0] for i in Login.currentlyrentedlist]
        indextocancel2 = templist2.index(returnedcart)
        del Login.currentlyrentedlist[indextocancel2]

        self.updateRented()
        self.updateAvailable()

    def removeCart(self):
        whichcart, ok = QInputDialog.getText(self, "Odebrat motokáru", "Zadejte číslo motokáry")
        if ok:
            self.available.takeItem(int(whichcart) - 1)

    def markAsDefective(self):
        cartnum, ok = QInputDialog.getText(self, "Označit nefunkční", "Zadejte číslo motokáry")
        if ok:
            templist = [i[0] for i in Login.availablelist]
            if int(cartnum) in templist:
                indextochange = templist.index(int(cartnum))
                Login.availablelist[indextochange][1] = 0
                self.updateAvailable()

    def markAsUsable(self):
        cartnum, ok = QInputDialog.getText(self, "Označit funkční", "Zadejte číslo motokáry")
        if ok:
            templist = [i[0] for i in Login.availablelist]
            if int(cartnum) in templist:
                indextochange = templist.index(int(cartnum))
                Login.availablelist[indextochange][1] = 1
                self.updateAvailable()

    def checkIfToReturn(self):
        timenow = datetime.now()
        currenttime = (timenow.hour * 60) + timenow.minute
        if not Login.currentlyrentedlist:
            pass
        else:
            if Login.currentlyrentedlist[0][1] == currenttime:
                Login.toreturnlist.append((Login.currentlyrentedlist[0][0]))
                del Login.currentlyrentedlist[0]
                self.updateRented()
                self.updateToReturn()
                self.checkIfToReturn()
            elif Login.currentlyrentedlist[0][1] != currenttime:
                pass

    def updateToReturn(self):
        if not Login.toreturnlist:
            self.toreturn.clear()
        else:
            self.toreturn.clear()

            for i in range(len(Login.toreturnlist)):
                cartwidget = QtWidgets.QListWidgetItem()

                customwidget = QtWidgets.QWidget()
                widgetButton = QtWidgets.QPushButton("Potvrdit vrácení motokáry " + str(Login.toreturnlist[i]))
                widgetButton.setAccessibleName(str(Login.toreturnlist[i]))
                widgetButton.clicked.connect(self.confirmReturn)
                widgetButton.setFixedWidth(355)
                widgetButton.setFixedHeight(41)
                widgetButton.setStyleSheet(
                    "QPushButton"
                    "{"
                    "color: black;"
                    "background-color: #b3befd;"
                    "border-style: solid;"
                    "border-width: 2px;"
                    "border-color: #000000"
                    "}"
                    "QPushButton::hover"
                    "{"
                    "background-color : #DFF9FD;"
                    "}"
                )
                widgetButton.setFont(QFont('Times', 15))

                customwidget.setStyleSheet(
                    "color: black;"
                    "background-color: #b3befd;"
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

                self.toreturn.insertItem(i, cartwidget)
                self.toreturn.setItemWidget(cartwidget, customwidget)

    def confirmReturn(self):
        returnclicked = self.sender()
        returnedcart = int(returnclicked.accessibleName())

        templist = [i[0] for i in Login.availablelist]
        whereto = bisect(templist, returnedcart)
        Login.availablelist.insert(whereto, [returnedcart, 1])

        indextocancel = Login.toreturnlist.index(returnedcart)
        del Login.toreturnlist[indextocancel]

        self.updateToReturn()
        self.updateAvailable()

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
