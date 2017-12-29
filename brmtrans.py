#!/usr/bin/python

import sys
import sqlite3
from fce import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEBUG=0

scb="Scan barcode now"

app=QApplication(sys.argv)
mainWidget=QWidget() 
mainWidget.resize(1280,1024)
mainWidget.setWindowTitle("BrmbarSAP - Transfer credit")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmTransfer(mw=None):
	if DEBUG: print("brmTransfer")
	lbls=mw.findChildren(QLabel)
	fr=lbls[-5]
	to=lbls[-2]
	le=mw.findChildren(QLineEdit)
	pswd=hashlib.sha512(brmSatanize(le[0].text())).hexdigest()
	amount=str(le[1].text())

	if amount=="0":
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_BADLE)
		return
	else:
		le[1].setStyleSheet(le[1].styleSheet()+STYLE_OKLE)

	# users set?
	if fr.text()==to.text() or fr.text()[0]=="<" or to.text()[0]=="<":
		return

	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	dbc.execute("SELECT id,cash,pass FROM users WHERE"
		" name='"+brmSatanize(fr.text())+"' LIMIT 1;")
	frdb=dbc.fetchone()
	if DEBUG: print("  "+str(frdb))

	if frdb[1]<=BUY_LIMIT:
		db.close()
		sys.exit(EXIT_NOCREDIT)
	if frdb[2]!=pswd:
		db.close()
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_BADLE)
		le[0].setText("")
		return
	else:
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_OKLE)

	dbc.execute("UPDATE users SET cash=cash-("+amount+") WHERE"
		" name='"+brmSatanize(fr.text())+"' LIMIT 1;")
	dbc.execute("UPDATE users SET cash=cash+("+amount+") WHERE"
		" name='"+brmSatanize(to.text())+"' LIMIT 1;")
	dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
		"(SELECT id FROM users WHERE name='"+str(fr.text())+"' LIMIT 1),0,1,"
		"-("+amount+"),0);")
	dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
		"(SELECT id FROM users WHERE name='"+str(to.text())+"' LIMIT 1),0,1,"
		"+("+amount+"),0);")
	db.commit()
	db.close()
	sys.exit(EXIT_TRANSFERRED)


def brmSetWho(val=""):
	if DEBUG: print("brmSetWho: code='"+val+"'")
	#le=mainWidget.findChildren(QLineEdit)[-1]
	if val=="":
		return

	lbls=mainWidget.findChildren(QLabel)
	fr=lbls[-5]
	to=lbls[-2]

	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	dbc.execute("SELECT name FROM users WHERE code='"+brmSatanize(val)+""
		"' LIMIT 1;")
	rec=dbc.fetchone()

	if DEBUG: print("  "+str(rec))
	if rec==None:
		return
	print("  "+fr.text())
	if fr.text()==scb:
		fr.setText(brmSatanize(rec[0]))
		to.setText(scb)
	else:
		to.setText(brmSatanize(rec[0]))
	db.close()


fbox=QHBoxLayout()
cf=QLabel("Credit from:")
cf.setStyleSheet(STYLE_TEXT)
fbox.addWidget(cf)
fbox.addStretch(1)
cf2=QLabel(scb)
cf2.setStyleSheet(STYLE_MSG+"margin-right:100px;")
fbox.addWidget(cf2)

pbox=QHBoxLayout()
pl=QLabel("Password (if set)")
pl.setStyleSheet(STYLE_TEXT)
pbox.addWidget(pl)
pbox.addStretch(1)
brmAddLine(pbox,"",'T',STYLE_LE,
	lambda:QTimer.singleShot(0,mainWidget.findChildren(QLineEdit)[-1],
		SLOT('setFocus()')),c=0)

tbox=QHBoxLayout()
ct=QLabel("Credit to:")
ct.setStyleSheet(STYLE_TEXT)
tbox.addWidget(ct)
tbox.addStretch(1)
ct2=QLabel("")
ct2.setStyleSheet(STYLE_MSG+"margin-right:100px;")
tbox.addWidget(ct2)

cbox=QHBoxLayout()
al=QLabel("Amount:")
al.setStyleSheet(STYLE_TEXT)
cbox.addWidget(al)
cbox.addStretch(1)
brmAddLine(cbox,"0","N1",STYLE_LE,
	lambda:QTimer.singleShot(0,mainWidget.findChildren(QLineEdit)[-1],
		SLOT('setFocus()')),c=0)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Transfer",lambda:brmTransfer(mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Transfer credit")
screenbox.addStretch(1)
screenbox.addLayout(fbox)
screenbox.addLayout(pbox)
screenbox.addStretch(1)
screenbox.addLayout(tbox)
screenbox.addStretch(1)
screenbox.addLayout(cbox)
screenbox.addStretch(5)
screenbox.addLayout(bbox)
brmAddLine(screenbox,"",'T',STYLE_HIDDEN,brmSetWho)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

mainWidget.findChildren(QLineEdit)[0].setEchoMode(2) # Password masking

app.exec_()
sys.exit(EXIT_CANCEL)
