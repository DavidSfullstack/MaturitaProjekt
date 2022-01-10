import sys
import os

from datetime import datetime
from bisect import bisect

import sqlite3

from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QInputDialog, QHBoxLayout, QPushButton, \
    QLineEdit, QMessageBox


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginFunction)

    def loginFunction(self):
        Login.user = self.name.text()
        tempcash = self.cash.text()

        if Login.user == "" or len(str(tempcash)) == "" or any([char.isdigit() for char in Login.user]):
            self.errormsg.setText("Vyplňte platné údaje")
        else:
            Login.money = int(tempcash)
            self.createDatabase()
            self.createLists()
            self.gotomainscreen()

            cashamountstart = str(Login.money)
            today = datetime.today().strftime('%d-%m-%Y')
            logfile = open("záznam.txt", "a")
            logfile.write(
               "\nDatum: " + today + "\nKasa začátek: " + cashamountstart + "Kč")
            logfile.close()

    def gotomainscreen(self):
        mainscreen = MainScreen()
        widget.addWidget(mainscreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createDatabase(self):
        if not os.path.exists("cartdata.db"):
            conn = sqlite3.connect('cartdata.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE carts (
                    cartnumber integer,
                    condition integer
                    )""")
            conn.commit()
            conn.close()
        if not os.path.exists("currvalues.db"):
            conn1 = sqlite3.connect('currvalues.db')
            c1 = conn1.cursor()
            c1.execute("""CREATE TABLE lastvalue(
                           price integer,
                          duration integer,
                          password text
                            )""")
            conn1.commit()
            c1.execute("""INSERT INTO lastvalue (price,duration,password) VALUES (30,30,'admin')""")
            conn1.commit()
            conn1.close()

    def createLists(self):
        conn = sqlite3.connect("cartdata.db")
        c = conn.cursor()
        c.execute("SELECT * FROM carts ORDER BY cartnumber")
        result = c.fetchall()
        Login.availablelist = []
        for i in range(len(result)):
            Login.availablelist.append([result[i][0], result[i][1]])
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
        updatetimer.timeout.connect(self.getValues)
        updatetimer.timeout.connect(self.displayCurrentValues)

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
        self.pricebutton.clicked.connect(self.changePrice)
        self.timebutton.clicked.connect(self.changeDuration)
        self.swapbutton.clicked.connect(self.swapCarts)
        self.passwordbutton.clicked.connect(self.changePassword)

    def getValues(self):
        conn1 = sqlite3.connect('currvalues.db')
        c1 = conn1.cursor()

        c1.execute("SELECT price FROM lastvalue")
        MainScreen.price = c1.fetchall()[0][0]

        c1.execute("SELECT duration FROM lastvalue")
        MainScreen.duration = c1.fetchall()[0][0]

        c1.execute("SELECT password FROM lastvalue")
        MainScreen.password = c1.fetchall()[0][0]
        conn1.close()

    def displayCurrentValues(self):
        self.currentduration.setText("Trvání: " + str(MainScreen.duration) + " min")
        self.currentduration.setAlignment(QtCore.Qt.AlignCenter)

        self.currentprice.setText("Cena: " + str(MainScreen.price) + "Kč")
        self.currentprice.setAlignment(QtCore.Qt.AlignCenter)

    def displayCashAmount(self):
        self.cashamount.setText("Stav kasy: " + str(Login.money))

    def displayTime(self):
        currenttime = QTime.currentTime()
        displaytime = currenttime.toString('hh:mm:ss')
        self.timer.setAlignment(QtCore.Qt.AlignCenter)
        self.timer.setText(displaytime)

    def addCart(self):
        checkrights, ok = QInputDialog.getText(self, "Přidat motokáru", "Zadejte heslo:", QLineEdit.Password)
        if ok and checkrights == MainScreen.password:
            cartnum, ok = QInputDialog.getInt(self, "Přidat motokáru", "Zadejte číslo motokáry")

            if ok:
                templist = [i[0] for i in Login.availablelist]
                templist1 = [i[0] for i in Login.currentlyrentedlist]
                if cartnum in templist or cartnum in templist1 or cartnum in Login.toreturnlist:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Motokára s tímto číslem již existuje")
                    msg.setWindowTitle("Duplikát")
                    msg.exec_()
                else:
                    where = bisect(templist, cartnum)
                    Login.availablelist.insert(where, [cartnum, 1])

                    conn = sqlite3.connect("cartdata.db")
                    c = conn.cursor()
                    c.execute("""INSERT INTO carts (cartnumber, condition)
                        VALUES (?, ?) 
                        """, (cartnum, 1))
                    conn.commit()

                    c.execute("SELECT * FROM carts ORDER BY cartnumber")

                    result = c.fetchall()

                    conn.close()

                    self.updateAvailable()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nesprávné heslo")
            msg.setInformativeText("Zkuste to znovu.")
            msg.setWindowTitle("Nesprávné heslo.")
            msg.exec_()

    def updateAvailable(self):
        if not Login.availablelist:
            self.available.clear()
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
        Login.money = Login.money + MainScreen.price

        timenow = datetime.now()
        timetoreturn = (timenow.hour * 60) + timenow.minute + MainScreen.duration

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
            widgetButton.setFixedWidth(138)
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
            widgetButton2.setFixedWidth(138)
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

            returnhour = Login.currentlyrentedlist[i][1]//60
            returnminute = Login.currentlyrentedlist[i][1] % 60
            disreturntime = str(returnhour) + ":"
            if returnminute < 10:
                disreturntime = disreturntime + "0" + str(returnminute)
            else:
                disreturntime = disreturntime + str(returnminute)

            widgetText = QtWidgets.QLabel(disreturntime)
            widgetText.setFixedWidth(67)
            widgetText.setFixedHeight(41)
            widgetText.setStyleSheet(
                "QLabel"
                "{"
                "color: black;"
                "background-color: #c9e0fd;"
                "border-style: solid;"
                "border-width: 2px;"
                "border-color: #000000"
                "}"
            )
            widgetText.setFont(QFont('Times', 15))
            widgetText.setAlignment(QtCore.Qt.AlignCenter)

            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addStretch()
            widgetLayout.addWidget(widgetButton)
            widgetLayout.addStretch()
            widgetLayout.addWidget(widgetButton2)
            widgetLayout.addStretch()
            widgetLayout.addWidget(widgetText)
            widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            customwidget.setLayout(widgetLayout)
            cartwidget.setSizeHint(customwidget.sizeHint())

            self.currentlyrented.insertItem(i, cartwidget)
            self.currentlyrented.setItemWidget(cartwidget, customwidget)

    def cancelRent(self):
        Login.money = Login.money - MainScreen.price
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
        checkrights, ok = QInputDialog.getText(self, "Odebrat motokáru", "Zadejte heslo:", QLineEdit.Password)
        if ok and checkrights == MainScreen.password:
            whichcart, ok = QInputDialog.getInt(self, "Odebrat motokáru", "Zadejte číslo motokáry")
            if ok:
                templist = [i[0] for i in Login.availablelist]
                if whichcart not in templist:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Ujistěte se, že je v prvním sloupci.")
                    msg.setWindowTitle("Motokára nenalezena.")
                    msg.exec_()
                else:
                    index = templist.index(whichcart)
                    del Login.availablelist[index]

                    conn = sqlite3.connect("cartdata.db")
                    c = conn.cursor()
                    query = ("DELETE FROM carts WHERE cartnumber=?")
                    c.execute(query, (whichcart,))
                    conn.commit()
                    conn.close()

                    self.updateAvailable()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nesprávné heslo")
            msg.setInformativeText("Zkuste to znovu.")
            msg.setWindowTitle("Nesprávné heslo.")
            msg.exec_()

    def markAsDefective(self):
        cartnum, ok = QInputDialog.getText(self, "Označit nefunkční", "Zadejte číslo motokáry")
        if ok:
            templist = [i[0] for i in Login.availablelist]
            if int(cartnum) in templist:
                indextochange = templist.index(int(cartnum))
                Login.availablelist[indextochange][1] = 0

                conn = sqlite3.connect("cartdata.db")
                c = conn.cursor()
                query = ("UPDATE carts SET condition=0 WHERE cartnumber=?")
                c.execute(query, (cartnum,))
                conn.commit()
                conn.close()

                self.updateAvailable()

    def markAsUsable(self):
        cartnum, ok = QInputDialog.getText(self, "Označit funkční", "Zadejte číslo motokáry")
        if ok:
            templist = [i[0] for i in Login.availablelist]
            if int(cartnum) in templist:
                indextochange = templist.index(int(cartnum))
                Login.availablelist[indextochange][1] = 1

                conn = sqlite3.connect("cartdata.db")
                c = conn.cursor()
                query = ("UPDATE carts SET condition=1 WHERE cartnumber=?")
                c.execute(query, (cartnum,))
                conn.commit()
                conn.close()

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
        logfile = open("záznam.txt", "a")
        logfile.write(
            "\nKasa konec: " + cashamountend + "Kč\nJméno: " + Login.user + "\n ")
        logfile.close()
        app.quit()

    def changePrice(self):
        checkrights, ok = QInputDialog.getText(self, "Změnit cenu", "Zadejte heslo:", QLineEdit.Password)
        if ok and checkrights == MainScreen.password:
            newprice, ok = QInputDialog.getInt(self, "Změnit cenu", "Nová cena:")
            if ok:
                conn1 = sqlite3.connect("currvalues.db")
                c1 = conn1.cursor()
                query = ("UPDATE lastvalue SET price=?")
                c1.execute(query, (newprice,))
                conn1.commit()
                conn1.close()

                MainScreen.price = newprice
                self.displayCurrentValues()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nesprávné heslo")
            msg.setInformativeText("Zkuste to znovu.")
            msg.setWindowTitle("Nesprávné heslo.")
            msg.exec_()

    def changeDuration(self):
        checkrights, ok = QInputDialog.getText(self, "Změnit trvání", "Zadejte heslo:", QLineEdit.Password)
        if ok and checkrights == MainScreen.password:
            time, ok = QInputDialog.getInt(self, "Změnit trvání", "Nová doba v min:")
            if ok:
                conn1 = sqlite3.connect("currvalues.db")
                c1 = conn1.cursor()
                query = ("UPDATE lastvalue SET duration=?")
                c1.execute(query, (time,))
                conn1.commit()
                conn1.close()

                MainScreen.duration = time
                self.displayCurrentValues()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nesprávné heslo")
            msg.setInformativeText("Zkuste to znovu.")
            msg.setWindowTitle("Nesprávné heslo.")
            msg.exec_()

    def swapCarts(self):
        cart1, ok = QInputDialog.getInt(self, "Prohodit motokáry", "První motokára:")

        if ok:
            cart2, ok = QInputDialog.getInt(self, "Prohodit motokáry", "Druhá motokára:")
            if ok:
                if cart1 in [i[0] for i in Login.availablelist] and cart2 in [i[0] for i in Login.availablelist]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Obě motokáry by měly být k dispozici.")
                    msg.setWindowTitle("Není důvod prohazovat.")
                    msg.exec_()

                elif cart1 in Login.toreturnlist and cart2 in Login.toreturnlist:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Obě motokáry by teď měly být vráceny.")
                    msg.setWindowTitle("Není důvod prohazovat.")
                    msg.exec_()

                elif cart1 in [i[0] for i in Login.availablelist] and cart2 in Login.toreturnlist:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Motokáry by teď měly být vráceny nebo jsou k dispozici.")
                    msg.setWindowTitle("Není důvod prohazovat.")
                    msg.exec_()

                elif cart1 in Login.toreturnlist and cart2 in [i[0] for i in Login.availablelist]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Motokáry by teď měly být vráceny nebo jsou k dispozici.")
                    msg.setWindowTitle("Není důvod prohazovat.")
                    msg.exec_()

                elif cart1 in [i[0] for i in Login.currentlyrentedlist] and cart2 in [i[0] for i in
                                                                                      Login.availablelist]:
                    index = [i[0] for i in Login.availablelist].index(cart2)
                    del Login.availablelist[index]

                    whereto = bisect([i[0] for i in Login.availablelist], cart1)
                    Login.availablelist.insert(whereto, [cart1, 1])

                    templist1 = [i[0] for i in Login.currentlyrentedlist]
                    index1 = templist1.index(cart1)
                    Login.currentlyrentedlist[index1][0] = cart2

                    self.updateAvailable()
                    self.updateRented()

                elif cart1 in [i[0] for i in Login.currentlyrentedlist] and cart2 in Login.toreturnlist:
                    index = Login.toreturnlist.index(cart2)
                    Login.toreturnlist[index] = cart1

                    templist1 = [i[0] for i in Login.currentlyrentedlist]
                    index1 = templist1.index(cart1)
                    Login.currentlyrentedlist[index1][0] = cart2

                    self.updateAvailable()
                    self.updateToReturn()
                    self.updateRented()

                elif cart1 in Login.toreturnlist and cart2 in [i[0] for i in Login.currentlyrentedlist]:
                    index = Login.toreturnlist.index(cart1)
                    Login.toreturnlist[index] = cart2

                    templist1 = [i[0] for i in Login.currentlyrentedlist]
                    index1 = templist1.index(cart2)
                    Login.currentlyrentedlist[index1][0] = cart1

                    self.updateToReturn()
                    self.updateRented()

                elif cart1 in [i[0] for i in Login.currentlyrentedlist] and cart2 in [i[0] for i in
                                                                                      Login.currentlyrentedlist]:
                    indexx = [i[0] for i in Login.currentlyrentedlist].index(cart1)
                    indexy = [i[0] for i in Login.currentlyrentedlist].index(cart2)
                    Login.currentlyrentedlist[indexx][0], Login.currentlyrentedlist[indexy][0] = \
                        Login.currentlyrentedlist[indexy][0], Login.currentlyrentedlist[indexx][0]
                    self.updateRented()

                elif cart1 in [i[0] for i in Login.availablelist] and cart2 in [i[0] for i in Login.currentlyrentedlist]:
                    index = [i[0] for i in Login.availablelist].index(cart1)
                    del Login.availablelist[index]

                    whereto = bisect([i[0] for i in Login.availablelist], cart2)
                    Login.availablelist.insert(whereto, [cart2, 1])

                    templist1 = [i[0] for i in Login.currentlyrentedlist]
                    index1 = templist1.index(cart2)
                    Login.currentlyrentedlist[index1][0] = cart1

                    self.updateAvailable()
                    self.updateRented()

    def changePassword(self):
        checkpass, ok = QInputDialog.getText(self, "Změnit heslo", "Zadejte aktuální heslo:", QLineEdit.Password)
        if ok and checkpass == MainScreen.password:
            newpass, ok = QInputDialog.getText(self, "Změnit heslo", "Zadejte nové heslo:")
            if ok:
                newpassconf, ok = QInputDialog.getText(self, "Změnit heslo", "Potvrďte nové heslo:")
                if ok and newpass == newpassconf:
                    conn1 = sqlite3.connect("currvalues.db")
                    c1 = conn1.cursor()
                    query = ("UPDATE lastvalue SET password=?")
                    c1.execute(query, (newpassconf,))
                    conn1.commit()
                    conn1.close()

                    MainScreen.password = newpassconf
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Hesla se neshodují")
                    msg.setInformativeText("Zkuste to znovu.")
                    msg.setWindowTitle("Hesla se neshodují.")
                    msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nesprávné heslo")
            msg.setInformativeText("Zkuste to znovu.")
            msg.setWindowTitle("Nesprávné heslo.")
            msg.exec_()


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
