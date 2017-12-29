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
mainWidget.setWindowTitle("BrmbarSAP - Receipt")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmReceipt(mw=None):
	if DEBUG:print("brmReceipt")
	le=mw.findChildren(QLineEdit)
	led=brmSatanize(le[0].text())
	lea=str(int(le[1].text()))
	leu=brmSatanize(le[2].text())
	lep=hashlib.sha512(brmSatanize(le[3].text())).hexdigest()

	if led=="":
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_BADLE)
		return
	else:
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_OKLE)
	if int(lea)<=0:
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_BADLE)
		return
	else:
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_OKLE)
	if leu=="":
		le[2].setStyleSheet(le[2].styleSheet()+STYLE_BADLE)
		return
	else:
		le[2].setStyleSheet(le[2].styleSheet()+STYLE_OKLE)


	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	dbc.execute("SELECT id,pass,name FROM users WHERE code='"+leu+"' LIMIT 1;")
	usr=dbc.fetchone()
	if DEBUG:print("  "+str(usr))
	if usr==None:
		db.close()
		le[2].setStyleSheet(le[2].styleSheet()+STYLE_BADLE)
		return
	else:
		le[2].setStyleSheet(le[2].styleSheet()+STYLE_OKLE)
	if usr[1]!=lep:
		db.close()
		le[3].setText("")
		le[3].setStyleSheet(le[3].styleSheet()+STYLE_BADLE)
		return
	else:
		le[3].setStyleSheet(le[3].styleSheet()+STYLE_OKLE)

	dbc.execute("SELECT (SELECT sum(profit) FROM transactions WHERE what=1)-"
		"(SELECT sum(cash) FROM users WHERE id>1);")
	ac=dbc.fetchone()
	if ac==None or float(ac[0])<1:
		db.close()
		brmPassMsg("No available money to spend")
		sys.exit(EXIT_MSG)

	if float(ac[0])<int(lea):
		db.close()
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_BADLE)
		return
	else:
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_OKLE)

	dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
		" "+str(usr[0])+",0,1,"+lea+",-"+lea+");")
	db.commit() # Must be before next statement
	dbc.execute("INSERT INTO receipts VALUES "
		"(NULL,"+str(dbc.lastrowid)+",'"+led+"');")
	db.commit()

	db.close()
	brmPassMsg(lea+" Kc charged to "+usr[2])
	sys.exit(EXIT_MSG)


dbox=QHBoxLayout()
dl=QLabel("Description")
dl.setStyleSheet(STYLE_TEXT)
dbox.addWidget(dl)
dbox.addStretch(1)
brmAddLine(dbox,"",'T',STYLE_LE,lambda:None,c=0,w=800)

sbox=QHBoxLayout()
al=QLabel("Amount")
al.setStyleSheet(STYLE_TEXT)
sbox.addWidget(al)
sbox.addStretch(1)
brmAddLine(sbox,"0",'N1',STYLE_LE,lambda:None,c=0)

ubox=QHBoxLayout()
ul=QLabel("Responsible user")
ul.setStyleSheet(STYLE_TEXT)
ubox.addWidget(ul)
ubox.addStretch(1)
brmAddLine(ubox,"",'T',STYLE_LE,lambda:None,c=0)

pbox=QHBoxLayout()
pl=QLabel("User password (if set)")
pl.setStyleSheet(STYLE_TEXT)
pbox.addWidget(pl)
pbox.addStretch(1)
brmAddLine(pbox,"","T",STYLE_LE,lambda:None,c=0)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Get paid",lambda:brmReceipt(mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Identify the receipt (ie 'BrmbarSAP - licence fee'),\n"
	"the amount from the receipt and responsible user.\n\n"
	"You can NOT withdraw more than available profit\n"
  "Invalid value is indicated by red background color")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Donation to brmlab")
screenbox.addStretch(1)
screenbox.addLayout(dbox)
screenbox.addStretch(1)
screenbox.addLayout(sbox)
screenbox.addStretch(1)
screenbox.addLayout(ubox)
screenbox.addLayout(pbox)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

mainWidget.findChildren(QLineEdit)[3].setEchoMode(2) # Password masking

app.exec_()
sys.exit(EXIT_CANCEL)
