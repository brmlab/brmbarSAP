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
mainWidget.setWindowTitle("BrmbarSAP - Edit stuff")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmStoreStock(mw=None):
	if DEBUG: print("brmStoreStock")
	s=mw.findChildren(QLineEdit)
	sname=brmSatanize(s[0].text())
	sam=int(s[1].text())
	sbuy=float(s[2].text())
	ssell=float(s[3].text())
	scode=s[4].text() # do NOT satanize!
	sid=brmSatanize(s[5].text())

	if ssell<sbuy or ssell>2*sbuy: # Check reasonable profit
		s[3].setStyleSheet(s[3].styleSheet()+STYLE_BADLE)
		return
	else:
		s[3].setStyleSheet(s[3].styleSheet()+STYLE_OKLE)

	if sname=="": # Name required
		s[0].setStyleSheet(s[0].styleSheet()+STYLE_BADLE)
		return
	else:
		s[0].setStyleSheet(s[0].styleSheet()+STYLE_OKLE)
	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()

	# Prevent 2 items with same name
	dbc.execute("SELECT id FROM stock WHERE name='"+sname+"';")
	dbn=dbc.fetchone()
	if dbn!=None and str(dbn[0])!=sid:
		db.close()
		s[0].setStyleSheet(s[0].styleSheet()+STYLE_BADLE)
		return
	else:
		s[0].setStyleSheet(s[0].styleSheet()+STYLE_OKLE)

	if sid=="0":
		dbc.execute("INSERT INTO stock VALUES (NULL,'"+sname+"',"
			" "+str(sam)+","+str(sbuy)+","+str(ssell)+");")
		lst=str(dbc.lastrowid)
	else:
		dbc.execute("UPDATE stock SET name='"+sname+"',"
			"quan=quan+("+str(sam)+"),buyprice="+str(sbuy)+","
			"sellprice="+str(ssell)+" WHERE id="+str(sid)+" LIMIT 1;")
		lst=sid
		dbc.execute("DELETE FROM barcodes WHERE stock="+sid+";")

	if scode!="":
		codes=scode.split(';')
		for cde in codes:
			dbc.execute("INSERT INTO barcodes VALUES (NULL,"+lst+",'"+str(cde)+"');")

	dbc.execute("INSERT INTO TRANSACTIONS VALUES(NULL,CURRENT_TIMESTAMP,1,"
		" "+sid+","+str(sam)+","+str(sbuy*sam)+",0);")

	db.commit()
	db.close()
	brmPassMsg("Stock saved! Take "+str(int(sam*sbuy))+" Kc")
	sys.exit(EXIT_MSG)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Save",lambda:brmStoreStock(mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

ename=QHBoxLayout()
ename.addStretch(1)
brmAddLine(ename,brmSatanize(sys.argv[2]),'T',STYLE_LE,None,c=0,foc=0,w=600)
ename.addStretch(1)

equan=QHBoxLayout()
al=QLabel("Restock (now "+str(int(brmSatanize(sys.argv[3])))+")")
al.setStyleSheet(STYLE_TEXT)
equan.addWidget(al)
equan.addStretch(1)
brmAddLine(equan,"0","N",STYLE_LE,None,c=0,foc=0)

ebuy=QHBoxLayout()
bl=QLabel("Buy price")
bl.setStyleSheet(STYLE_TEXT)
ebuy.addWidget(bl)
ebuy.addStretch(1)
brmAddLine(ebuy,str(float(brmSatanize(sys.argv[4]))),
	"Q+",STYLE_LE,None,c=0,foc=0)

esell=QHBoxLayout()
sl=QLabel("Sell price")
sl.setStyleSheet(STYLE_TEXT)
esell.addWidget(sl)
esell.addStretch(1)
brmAddLine(esell,str(float(brmSatanize(sys.argv[5]))),
	"Q+",STYLE_LE,None,c=0,foc=0)

ecode=QHBoxLayout()
cl=QLabel("Barcodes")
cl.setStyleSheet(STYLE_TEXT)
ecode.addWidget(cl)
ecode.addStretch(1)
brmAddLine(ecode,"","T",STYLE_LE,None,c=0,foc=0)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Restock existing stuff or enter new one\n\n"
	"'Buy price' is the price you want to get back for 1 item\n"
	"'Sell price' is the price for which brmbar will sell 1 item\n"
	"Set 'Sell' higher than 'Buy price' - give brmbar reasonable profit\n\n"
	"Put cursor to 'Barcodes' and scan the barcode of the item\n"
	"If there are more different barcodes, split them by ';'\n\n"
  "Invalid value is indicated by red background color")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Edit item")
screenbox.addLayout(ename)
screenbox.addLayout(equan)
screenbox.addLayout(ebuy)
screenbox.addLayout(esell)
screenbox.addLayout(ecode)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)
# Stores ID of the stock or NULL if new stuff - do nothing, button does it
brmAddLine(screenbox,brmSatanize(sys.argv[1]),'T',STYLE_HIDDEN,None)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

levalue4=mainWidget.findChildren(QLineEdit)[4]

db=sqlite3.connect(BRMDB)
dbc=db.cursor()
for c in dbc.execute("SELECT code FROM barcodes WHERE stock="
	""+brmSatanize(sys.argv[1])+";"):
	if levalue4.text()=="":
		levalue4.setText(brmSatanize(str(c[0])))
	else:
		levalue4.setText(levalue4.text()+","+brmSatanize(c[0]))
db.close()

app.exec_()
sys.exit(EXIT_CANCEL)
