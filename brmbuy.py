#!/bin/python

import sys
import sqlite3
from fce import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEBUG=0

db=sqlite3.connect(BRMDB)
dbc=db.cursor()
dbc.execute("SELECT * FROM stock WHERE id=("
	"SELECT stock FROM barcodes WHERE code='"+brmSatanize(sys.argv[1])+"')"
	"LIMIT 1;")
dbrec=dbc.fetchone()
db.close()
if DEBUG: print("DBREC="+str(dbrec))
if dbrec==None:
	sys.exit(EXIT_NOBARCODE)

app=QApplication(sys.argv)
mainWidget=QWidget() 
mainWidget.resize(1280,1024)
mainWidget.setWindowTitle("BrmbarSAP - BuyScreen")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmSetAmount(foo=None):
	if DEBUG: print("brmSetAmount")
	res=mainWidget.findChildren(QLineEdit)
	if res[0].text()=="0":
		res[0].setStyleSheet(res[0].styleSheet()+STYLE_BADLE)
	else:
		res[0].setStyleSheet(res[0].styleSheet()+STYLE_OKLE)
	QTimer.singleShot(0,res[-1],SLOT('setFocus()'))

def brmPayCash(dbrec=None,a=None):
	ale=a.findChildren(QLineEdit)[0]
	le=str(ale.text())
	sum=str(int(le)*int(dbrec[4]))
	profit=str(int(sum)-(int(le)*int(dbrec[3])))
	if DEBUG: print("brmPayCash: a="+le+"\n"
		"  "+str(dbrec[0]))

	if int(le)==0:
		ale.setStyleSheet(ale.styleSheet()+STYLE_BADLE)
		return
	else:
		ale.setStyleSheet(ale.styleSheet()+STYLE_OKLE)
	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
		"0,"+str(dbrec[0])+","+le+","+sum+","+profit+");")
	dbc.execute("UPDATE stock SET quan=quan-"+le+" WHERE id="+str(dbrec[0])+";")
	db.commit()
	db.close()

	brmPassMsg("Sold! Put "+str(int(le)*dbrec[4])+" to cashbox")
	sys.exit(EXIT_MSG)

def brmPayMember(dbrec=None,a=None):
	ale=a.findChildren(QLineEdit)[0]
	le=str(ale.text())
	apswd=a.findChildren(QLineEdit)[1]
	pswd=brmSatanize(apswd.text())

	sum=str(int(le)*int(dbrec[4]))
	profit=str(int(sum)-(int(le)*int(dbrec[3])))
	who=brmSatanize((a.findChildren(QLineEdit)[-1]).text())
	if DEBUG: print("brmPayMember: a="+le+" who='"+who+"'\n"
		"  "+str(dbrec))
	if who=="": # Just enter, ignore
		return
	if int(le)==0:
		ale.setStyleSheet(ale.styleSheet()+STYLE_BADLE)
		return
	else:
		ale.setStyleSheet(ale.styleSheet()+STYLE_OKLE)
	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()
	dbc.execute("SELECT * FROM users WHERE code='"+who+"' LIMIT 1;")
	whoid=dbc.fetchone()
	if DEBUG: print("  whoid="+str(whoid))
	if whoid==None:
		db.close()
		apswd.setText("")
		return
	if hashlib.sha512(pswd).hexdigest()!=whoid[4]:
		db.close()
		apswd.setText("")
		apswd.setStyleSheet(apswd.styleSheet()+STYLE_BADLE)
		return
	else:
		apswd.setStyleSheet(apswd.styleSheet()+STYLE_OKLE)

	if whoid[2]<BUY_LIMIT and int(sum)>0: # Allow buy negative price (ex. uklid)
		db.close()
		sys.exit(EXIT_NOCREDIT)

	dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
		" "+str(whoid[0])+","+str(dbrec[0])+","+le+","+sum+","+profit+");")
	dbc.execute("UPDATE stock SET quan=quan-"+le+" WHERE id="+str(dbrec[0])+";")
	dbc.execute("UPDATE users SET cash=cash-("+sum+") "
		"WHERE id='"+str(whoid[0])+"';")
	db.commit()
	db.close()

	brmPassMsg("'"+brmSatanize(dbrec[1])+"' sold to '"+brmSatanize(whoid[1])+"'")
	sys.exit(EXIT_MSG)


sbox=QHBoxLayout()
wl=QLabel(brmSatanize(dbrec[1]))
wl.setStyleSheet(STYLE_TEXT)
sbox.addWidget(wl)
sbox.addStretch(1)
wp=QLabel(str(dbrec[4])+" * ")
wp.setStyleSheet(STYLE_TEXT)
sbox.addWidget(wp)
brmAddLine(sbox,"1",'N1',STYLE_LE,brmSetAmount,c=0)

pbox=QHBoxLayout()
pl=QLabel("Password (if set)")
pl.setStyleSheet(STYLE_TEXT)
pbox.addWidget(pl)
pbox.addStretch(1)
brmAddLine(pbox,"","T",STYLE_LE,lambda:QTimer.singleShot(0,
	mainWidget.findChildren(QLineEdit)[-1],SLOT('setFocus()')),c=0)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Pay by cash",lambda:brmPayCash(dbrec,mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Set the required amount you want to buy.\n\n"
	"You can either 'Pay by cash', or scan your barcode to pay by credit\n\n"
	"Invalid value is indicated by red background color")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Transaction overview")
screenbox.addStretch(1)
screenbox.addLayout(sbox)
screenbox.addStretch(1)
screenbox.addLayout(pbox)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)
brmAddLine(screenbox,"",'T',STYLE_HIDDEN,lambda:brmPayMember(dbrec,mainWidget))

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

mainWidget.findChildren(QLineEdit)[1].setEchoMode(2) # Password masking

app.exec_()
sys.exit(EXIT_CANCEL)

