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
mainWidget.setWindowTitle("BrmbarSAP - Edit user")
mainWidget.setStyleSheet(STYLE_WIDGET)

said=str(int(sys.argv[1]))
san=brmSatanize(sys.argv[2])
sac=str(float(sys.argv[3]))
sam=brmSatanize(sys.argv[4])

def brmStoreUser(mw=None):
	if DEBUG: print("brmStoreUser")

	le=mw.findChildren(QLineEdit)
	leid=str(le[-1].text())
	lename=brmSatanize(le[0].text())
	lecash=str(le[1].text())
	lepass=hashlib.sha512(brmSatanize(le[2].text())).hexdigest()
	lenewpass=hashlib.sha512(brmSatanize(le[3].text())).hexdigest()
	lemail=str(le[4].text())

	if lename=="":
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_BADLE)
		return
	else:
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_OKLE)
	if lecash=="":
		lecash="0"

	db=sqlite3.connect(BRMDB)
	dbc=db.cursor()

	# Usename already used?
	dbc.execute("SELECT id FROM users WHERE name='"+lename+"';")
	cname=dbc.fetchone()
	if cname!=None and str(cname[0])!=leid:
		db.close()
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_BADLE)
		return
	else:
		le[0].setStyleSheet(le[0].styleSheet()+STYLE_OKLE)

	if leid=="0": # New user?
		dbc.execute("INSERT INTO users VALUES (NULL,'"+lename+"',"+lecash+","
			"'"+lename+"','"+lenewpass+"','"+lemail+"');")
		db.commit() # Sync required before next insert
		if lecash!="0": # New credit?
			dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
				"(SELECT id FROM users WHERE name='"+lename+"' LIMIT 1),"
				"0,1,"+lecash+",0);")
	else: # Existing user
		dbc.execute("SELECT pass,cash FROM users WHERE id="+leid+" LIMIT 1;")
		pswddb=dbc.fetchone()
		if lepass!=pswddb[0] and pswddb[0]!=NULL512:
			db.close()
			le[2].setText("")
			le[2].setStyleSheet(le[2].styleSheet()+STYLE_BADLE)
			return
		else:
			le[2].setStyleSheet(le[2].styleSheet()+STYLE_OKLE)

		if lename!="sachy_overflow": # Allow overflowers ignore the limit
			if ((int(pswddb[1])<BUY_LIMIT and int(lecash)<0) or
				int(pswddb[1])+int(lecash)<BUY_LIMIT):
				le[1].setStyleSheet(le[1].styleSheet()+STYLE_BADLE)
				db.close()
				return
			else:
				le[1].setStyleSheet(le[1].styleSheet()+STYLE_OKLE)
		
		if lecash!="0": # Charge/withdrawal?
			dbc.execute("INSERT INTO transactions VALUES (NULL,CURRENT_TIMESTAMP,"
				" "+leid+",0,1,"+lecash+",0);")

		zasranypython=" " if lenewpass==NULL512 else "pass='"+lenewpass+"',"
		dbc.execute("UPDATE users SET name='"+lename+"',cash=cash+("+lecash+"),"
			" "+zasranypython+" code='"+lename+"', mail='"+lemail+"' "
			"WHERE id="+leid+" LIMIT 1;")
	db.commit()
	db.close()
	sys.exit(EXIT_USER)


bbox=QHBoxLayout()
bbox.addStretch(1)
brmAddButton(bbox,"Save",lambda:brmStoreUser(mainWidget))
bbox.addStretch(1)
brmAddButton(bbox,"Cancel",lambda:sys.exit(EXIT_CANCEL))
bbox.addStretch(1)

ename=QHBoxLayout()
ename.addStretch(1)
brmAddLine(ename,san,
	'T',STYLE_LE,None,c=0,foc=0,w=800)
ename.addStretch(1)

ecash=QHBoxLayout()
cl=QLabel("Charge credit (now "+sac+")")
cl.setStyleSheet(STYLE_TEXT)
ecash.addWidget(cl)
ecash.addStretch(1)
brmAddLine(ecash,"0","N",STYLE_LE,None,c=0,foc=0)

ecode=QHBoxLayout()
bl=QLabel("Assigned barcode")
bl.setStyleSheet(STYLE_TEXT)
ecode.addWidget(bl)
ecode.addStretch(1)
bl2=QLabel(san)
bl2.setStyleSheet(STYLE_TEXT+"margin-right:100px;")
ecode.addWidget(bl2)

epass=QHBoxLayout()
pl=QLabel("Password (if set)")
pl.setStyleSheet(STYLE_TEXT)
epass.addWidget(pl)
epass.addStretch(1)
brmAddLine(epass,"","T",STYLE_LE,None,c=0,foc=0)

enpass=QHBoxLayout()
pnl=QLabel("New password?")
pnl.setStyleSheet(STYLE_TEXT)
enpass.addWidget(pnl)
enpass.addStretch(1)
brmAddLine(enpass,"","T",STYLE_LE,None,c=0,foc=0)

email=QHBoxLayout()
pm=QLabel("Send daily reports to:")
pm.setStyleSheet(STYLE_TEXT)
email.addWidget(pm)
email.addStretch(1)
brmAddLine(email,sam,'M',STYLE_LE,None,c=0,foc=0,w=500)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Fill out name for a new user or edit the existing one\n\n"
	"You can 'Charge' or 'Withdraw' credit by adding/substracting the Credit\n\n"
	"If you are setting the password for the 1st time, leave the upper clear\n\n"
	"Fill your mail to receive daily transaction reports\n\n"
  "Invalid value is indicated by red background color")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Edit user")
screenbox.addLayout(ename)
screenbox.addLayout(ecash)
screenbox.addLayout(ecode)
screenbox.addLayout(epass)
screenbox.addLayout(enpass)
screenbox.addLayout(email)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)
brmAddLine(screenbox,said,'T',STYLE_HIDDEN,None)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

pf=mainWidget.findChildren(QLineEdit)
pf[2].setEchoMode(2) # Password masking
pf[3].setEchoMode(2)

app.exec_()
sys.exit(EXIT_CANCEL)
