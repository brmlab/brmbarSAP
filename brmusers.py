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
mainWidget.setWindowTitle("BrmbarSAP - Manage users")
mainWidget.setStyleSheet(STYLE_WIDGET)

def brmEditUser(widget=None,code=None,id=None):
	if code==None: # Invoked from scanner?
		if widget==None: # Actually... new user?
			code=""
		else:
			code=brmSatanize((widget.findChildren(QLineEdit)[0]).text())
		if DEBUG: print("brmEditUser code="+str(code))
	if code==None: # scanner passed EOL only (no data)
		return
	# code="" -> New user
	# code="xyz" -> Edit existing user

	if code=="":
		usr=[0,"New user",0,""]
	else:
		db=sqlite3.connect(BRMDB)
		dbc=db.cursor()
		if id!=None: # If ID is known, use it
			dbc.execute("SELECT id,name,cash,mail FROM users "
				"WHERE id="+str(int(id))+" LIMIT 1;")
		else:
			dbc.execute("SELECT id,name,cash,mail FROM users "
				"WHERE code='"+code+"' LIMIT 1;")
		usr=dbc.fetchone()
		db.close()
		if usr==None:
			return
	if DEBUG: print("  "+str(usr))
	rc=os.system(str("python ./brmedituser.py "
		"'"+str(int(usr[0]))+"' "
		"'"+brmSatanize(usr[1])+"' "
		"'"+str(float(usr[2]))+"' "
		"'"+brmSatanize(usr[3])+"'"))
	sys.exit(rc>>8)

def brmAddListLayout(p=None,wat=None):
	if DEBUG: print("brmAddListLayout: '"+str(wat)+"'")
	line=QHBoxLayout()
	if wat==None:
		nu=QLabel("No users found!")
		nu.setStyleSheet(STYLE_TEXT)
		line.addWidget(nu)
	else:
		brmAddButton(line,brmSatanize(wat[1]),
			lambda:brmEditUser(mainWidget,str(wat[3]),str(wat[0])),
				s="margin-left:100px;")
		line.addStretch(1)
		cl=QLabel(str(float(wat[2])))
		cl.setStyleSheet(STYLE_TEXT+"margin-right:100px;")
		line.addWidget(cl)
	p.addLayout(line)

bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"New user",lambda:brmEditUser(None,None,None))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

db=sqlite3.connect(BRMDB)
dbc=db.cursor()
# Ignore "Cash" and "Replenishment" users (internal only)
dbusr=dbc.execute("SELECT * FROM users WHERE id>1 ORDER BY name ASC;")

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
db.close() # Must be closed AFTER the list is completed

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Users")
screenbox.addWidget(sbox)
screenbox.addLayout(bbox)
brmAddLine(screenbox,"",'T',STYLE_HIDDEN,
	lambda:brmEditUser(mainWidget,None,None))

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

app.exec_()

sys.exit(EXIT_CANCEL)
