#!/usr/bin/python

import sys
import sqlite3
from fce import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEBUG=0

app=QApplication(sys.argv)
mainWidget=QWidget() 

mainWidget.resize(1280,1024)
mainWidget.setWindowTitle("BrmbarSAP - Donation")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmDonate(mw=None,c=0):
	if DEBUG: print("brmDonate")
	les=mw.findChildren(QLineEdit)
	cash=str(les[0].text())
	pswd=hashlib.sha512(brmSatanize(les[1].text())).hexdigest()
	code=brmSatanize(les[-1].text())

	if cash=="0":
		les[0].setStyleSheet(les[0].styleSheet()+STYLE_BADLE)
		return
	else:
		les[0].setStyleSheet(les[0].styleSheet()+STYLE_OKLE)

	if code=="" and c==1:
		return # Accidental double-enter
	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	if code!="":
		dbc.execute("SELECT id,cash,pass FROM users WHERE"
			" code='"+code+"' LIMIT 1;")
		usr=dbc.fetchone()
		if usr==None:
			les[-1].setText("")
			db.close()
			return
		if usr[1]<=BUY_LIMIT:
			db.close()
			sys.exit(EXIT_NOCREDIT)
		if usr[2]!=pswd:
			db.close()
			les[1].setStyleSheet(les[1].styleSheet()+STYLE_BADLE)
			return
		else:
			les[1].setStyleSheet(les[1].styleSheet()+STYLE_OKLE)

		dbc.execute("UPDATE users SET cash=cash-"+cash+" WHERE id="+str(usr[0])+""
			" LIMIT 1;")
		dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP"
			","+str(usr[0])+",1,1,"+cash+","+cash+");")
	else:
		dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP"
			",0,1,1,"+cash+","+cash+");")
	db.commit()
	db.close()

	sys.exit(EXIT_DONATION)

sbox=QHBoxLayout()
al=QLabel("Amount")
al.setStyleSheet(STYLE_TEXT)
sbox.addWidget(al)
sbox.addStretch(1)
brmAddLine(sbox,"0",'N0',STYLE_LE,lambda:QTimer.singleShot(0,
	mainWidget.findChildren(QLineEdit)[-1],SLOT('setFocus()')),c=0)

pbox=QHBoxLayout()
pl=QLabel("User password (if set)")
pl.setStyleSheet(STYLE_TEXT)
pbox.addWidget(pl)
pbox.addStretch(1)
brmAddLine(pbox,"","T",STYLE_LE,lambda:QTimer.singleShot(0,
	mainWidget.findChildren(QLineEdit)[-1],SLOT('setFocus()')),c=0)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Donate cash",lambda:brmDonate(mainWidget,0))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Set the required amount you want to donate to brmlab.\n\n"
  "You can either 'Donate cash', or scan your barcode to donate credit\n\n"
  "Invalid value is indicated by red background color")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Donation to brmlab")
screenbox.addStretch(1)
screenbox.addLayout(sbox)
screenbox.addStretch(1)
screenbox.addLayout(pbox)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)
brmAddLine(screenbox,"",'T',STYLE_HIDDEN,lambda:brmDonate(mainWidget,1))

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

mainWidget.findChildren(QLineEdit)[1].setEchoMode(2) # Password masking

app.exec_()
sys.exit(EXIT_CANCEL)
