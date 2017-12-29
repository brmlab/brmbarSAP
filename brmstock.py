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
mainWidget.setWindowTitle("BrmbarSAP - Manage stock")
mainWidget.setStyleSheet(STYLE_WIDGET)

msg=QLabel("")
t=QTimer()

def brmEditStock(widget=None,code=None,id=None,mw=None):
	le=mw.findChildren(QLineEdit)[-1]
	if code==None: # Invoked from scanner?
		if widget==None: # Actually... new user?
			code=""
		else:
			code=brmSatanize(le.text())
	if DEBUG: print("brmEditStock code='"+str(code)+"'")
	if code==None: # scanner passed EOL only (no data)
		return
	# code="" -> New stuff
	# code="xyz" -> Edit existing stuff
	if code=="":
		usr=[0,"Stuff",0,0,0]
	else:
		db=sqlite3.connect(BRMDB)
		dbc=db.cursor()
		if id!=None: # If ID is known, use it
			dbc.execute("SELECT * FROM stock WHERE id="+str(int(id))+" LIMIT 1;")
		else: # If code is known, use it
			dbc.execute("SELECT * FROM stock WHERE id=("
				"SELECT stock FROM barcodes WHERE code='"+code+"' LIMIT 1) "
				"LIMIT 1;")
		usr=dbc.fetchone()
		db.close()
		if usr==None:
			return
	if DEBUG: print("  "+str(usr))

	rc=os.system(str("python ./brmeditstock.py "
		"'"+str(usr[0])+"' "
		"'"+brmSatanize(usr[1])+"' "
		"'"+str(usr[2])+"' "
		"'"+str(usr[3])+"' "
		"'"+str(usr[4])+"'"))
	brmParseRC(rc,msg,t,foc=le)
	print("aaaaaaa")
	(mw.findChildren(QLineEdit)[-1]).setFocus(True)
#	sys.exit(rc>>8)

def brmAddListLayout(p=None,wat=None):
	if DEBUG: print("brmAddListLayout: '"+str(wat)+"'")
	line=QHBoxLayout()
	if wat==None:
		nif=QLabel("No items found!")
		nif.setStyleSheet(STYLE_TEXT)
		line.addWidget(nif)
	else:
		brmAddButton(line,brmSatanize(wat[1]),
			lambda:brmEditStock(mainWidget,str(wat[3]),str(wat[0]),mainWidget),
				s="margin-left:100px;")
		line.addStretch(1)
		pl=QLabel(str(wat[4])+" Kc; #"+str(wat[2]))
		pl.setStyleSheet(STYLE_TEXT+"margin-right:100px;")
		line.addWidget(pl)
	p.addLayout(line)

msgbox=QHBoxLayout()
msgbox.addStretch(1)
msg.setStyleSheet(STYLE_MSG)
msg.setFocusPolicy(0)
msgbox.addWidget(msg)
msgbox.addStretch(1)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"New stuff",lambda:brmEditStock(None,None,None,mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

db=sqlite3.connect(BRMDB)
dbc=db.cursor()
# id=0 -> Charge credit
# id=1 -> Donation
dbusr=dbc.execute("SELECT * FROM stock WHERE id>1 ORDER BY name ASC;")

sbox=QScrollArea()
sbox.setWidgetResizable(True)
sbox.setFocusPolicy(0)
sboxList=QWidget(sbox)
sboxList.setFocusPolicy(0)
sboxLayout=QVBoxLayout(sboxList)
sboxList.setLayout(sboxLayout)
for row in dbusr:
	brmAddListLayout(sboxLayout,row)
sbox.setWidget(sboxList)
sbox.setStyleSheet(sbox.styleSheet()+"max-width:1200px")
db.close() # Must be closed AFTER the list is completed


screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Stock")
screenbox.addLayout(msgbox)
screenbox.addWidget(sbox)
screenbox.addLayout(bbox)
brmAddLine(screenbox,"",'T',STYLE_HIDDEN,
	lambda:brmEditStock(mainWidget,None,None,mainWidget),foc=1)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()



app.exec_()
sys.exit(EXIT_CANCEL)
