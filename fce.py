import os
import sys
import sqlite3
import hashlib
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *
from datetime import datetime

STYLE_BTN=("background-color:rgba(0,0,0,100);color:yellow;font-size:48px;"
	"border: 1px solid #217777;padding:5px;")
#STYLE_DESC="color:green;font-size:48px"
STYLE_LABEL="color:green;font-size:64px;"
STYLE_LE=("background-color:white;color:black;font-size:48px;"
	"margin-right:100px;")
STYLE_BADLE="background-color:red;" # Invalid data indicator
STYLE_OKLE="background-color:white;" # Fixed data indicator
#STYLE_ITEM="color:white;font-size:64px"
STYLE_HIDDEN="background-color:rgba(0,0,0,255);color:white;"     #rgba(0,0,0,255);"
STYLE_WIDGET="background-color:black;color:white;"
STYLE_MSG="background-color:black;color:yellow;font-size:32px;"
STYLE_TEXT=("background-color:black;color:white;font-size:48px;"
	"margin-left:100px;")
STYLE_HELP=("background-color:black;color:#217777;font-size:32px;")


EXIT_OK=0
EXIT_CANCEL=1
EXIT_MSG=2
EXIT_NOBARCODE=3
EXIT_NOCREDIT=4
EXIT_USER=5
EXIT_STOCKSAVED=6
EXIT_TRANSFERRED=7
EXIT_DONATION=8

MSGS=["Done!",
	"Transaction cancelled",
	"", # Reserved for external msg
	"Unknown barcode",
	"FAIL! Credit too low\nPlease recharge",
	"User saved",
	"Stock saved",
	"Credit transferred",
	"Thanks for the donation!"]
MSGFILE="/dev/shm/brmbarsap_msg"

BRMDB="./brmbar.db"

BUY_LIMIT=-200

# hashlib.sha512(brmSatanize("")).hexdigest()
NULL512=("cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce"
	"9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e")

DEBUG=1

# ====================================================================

def brmParseRC(rc=0,msg=None,t=None,foc=None):
	# Magic ahead:
	#   The Return Code is 16bit integer but we need only the HIGH byte
	rc=rc>>8
	if DEBUG: print("brmParseRC="+str(rc)+"='"+MSGS[rc]+"'")
	if rc==EXIT_MSG:
		fr=open(MSGFILE,"r")
		fmsg=fr.readline()
		if DEBUG: print("  FILEMSG: '"+fmsg+"'")
		msg.setText(fmsg)
		fr.close()
		os.remove(MSGFILE)
	else:
		msg.setText(MSGS[rc])
	t.start(5000)
	t.timeout.connect(lambda:msg.setText(""))
	if foc!=None:
		if DEBUG:print(str(foc))
		QTimer.singleShot(0,foc,SLOT('setFocus()'))
	return

# Sanitize string
def brmSatanize(s=""):
	ss=""
	sss=""
	try:
		ss=s.toAscii()
	except:
		for c in s:
			ss=ss+c.encode("ascii","ignore")

	for c in ss:
		if ord(c) > 31 and ord(c) < 127:
			sss=sss+c
	ss=sss
	ss=ss.replace("'","")
	ss=ss.replace("\"","")
	ss=ss.replace(";","")
	ss=ss.replace("`","")
	ss=ss.replace("<","")
	ss=ss.replace(">","")
	ss=ss.replace("$(","$ (")
	if DEBUG: print("brmSatanize:\n  "+ss)
	return str(ss);

# Clear Lineedit And Pass
def brmCLAP(le=None,f=None,c=1,foc=1):
	if DEBUG: print("brmCLAP")
	a=le.text()
	if c==1:
		le.setText("")
	try:
		f(a)
	except: # Revert the value
		le.setText(a)
		f()
		if c==1:
			le.setText("")
	if foc==1:
		QTimer.singleShot(0,le,SLOT('setFocus()'))
		le.setFocus(True)

timetimer=QTimer()
def brmLabelBox(p=None,lbl=""):
	if DEBUG: print("brmLabelBox: '"+lbl+"'")
	b=QHBoxLayout()
	b.addWidget(QSvgWidget("./brmlab.svg"))
	b.addStretch(1)
	b.addWidget(QLabel("<font style='"+STYLE_LABEL+"'>"+lbl+"</font>"))
	b.addStretch(1)
	timetext=("<font style='"+STYLE_MSG+"'>"
		""+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')+"</font>")
	timewidget=QLabel(timetext)
	timetimer.timeout.connect(
		lambda:timewidget.setText("<font style='"+STYLE_MSG+"'>"
		""+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')+"</font>"))
	timetimer.start(1000)
	b.addWidget(timewidget)
	p.addLayout(b)
def brmAddButton(p=None,lbl="",f=exit,w=0,s=""):
	if DEBUG: print("addBrmButton: '"+lbl+"'")
	butt=QPushButton(lbl)
	if int(w)>0:
		butt.setStyleSheet(STYLE_BTN+s+"text-align:left;"
			"width:"+str(int(w))+"px;max-width:"+str(int(w))+"px;")
	else:
		butt.setStyleSheet(STYLE_BTN+s)
	butt.connect(butt,SIGNAL('pressed()'),f)
	butt.setAutoDefault(0)
	butt.setFocusPolicy(0)
	p.addWidget(butt)

def brmAddLine(p=None,lbl="",r='T',s="",f=exit,w=200,c=1,foc=1):
	if DEBUG: print("addBrmLine: '"+str(lbl)+"'")
	l=QLineEdit(str(lbl))
	l.setStyleSheet(s+"width:"+str(w)+"px;max-width:"+str(w)+"px;")

#	if r=="T":
#		l.setValidator(QRegExpValidator(QRegExp("^[\d\s\w]*$")))
	if r=="Q":
		l.setValidator(QRegExpValidator(QRegExp("^-?[0-9]{1,5}(\.[0-9]{1,2})?$")))
	if r=="Q+":
		l.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,5}(\.[0-9]{0,2})?$")))
	if r=="N":
#		l.setValidator(QIntValidator(-100000,100000))
		l.setValidator(QRegExpValidator(QRegExp("^-?[0-9]{1,5}$")))
	if r=="N1":
#		l.setValidator(QIntValidator(1,100000))
		l.setValidator(QRegExpValidator(QRegExp("^[1-9]{1}[0-9]{0,4}$")))
	if r=="N0":
#		l.setValidator(QIntValidator(0,100000))
		l.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,5}$")))
	if r=="M":
		l.setValidator(QRegExpValidator(
			QRegExp("^[0-9A-Za-z\._-]{1,}@[0-9a-zA-Z\._-{1,}\.[a-zA-Z0-9]{1,}$")))

	l.connect(l,SIGNAL('returnPressed()'),lambda:brmCLAP(l,f,c,foc))
	if s==STYLE_HIDDEN:
		l.setFocusPolicy(Qt.StrongFocus)
		QTimer.singleShot(0,l,SLOT('setFocus()'))
	p.addWidget(l)

def brmPassMsg(s=""):
	fw=open(MSGFILE,"w")
	fw.write(s)
	fw.close()

