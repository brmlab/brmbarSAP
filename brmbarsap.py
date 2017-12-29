#!/usr/bin/python

import sys
import sqlite3
from fce import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEBUG=1

app=QApplication(sys.argv)
msg=QLabel("")
t=QTimer()

def brmStock():
	if DEBUG: print("brmStock")
	rc=os.system(str("python ./brmstock.py"))
	brmParseRC(rc,msg,t)
	return
def brmUsers():
	if DEBUG: print("brmUsers")
	rc=os.system(str("python ./brmusers.py"))
	brmParseRC(rc,msg,t)
	return
def brmBuy(wat=""):
	if DEBUG: print("brmBuy: '"+wat+"'")
	rc=os.system(str("python ./brmbuy.py '"+wat+"'"))
	brmParseRC(rc,msg,t)
	return
def brmTransfer():
	if DEBUG: print("brmTransfer")
	rc=os.system(str("python ./brmtrans.py"))
	brmParseRC(rc,msg,t)
	return
def brmDonate():
	if DEBUG: print("brmTansfer")
	rc=os.system(str("python ./brmdon.py"))
	brmParseRC(rc,msg,t)
	return
def brmReceipt():
	if DEBUG: print("brmReceipt")
	rc=os.system(str("python ./brmrec.py"))
	brmParseRC(rc,msg,t)
	return

mainWidget=QWidget() 
mainWidget.resize(1280,1024)
mainWidget.setWindowTitle("BrmbarSAP")
mainWidget.setStyleSheet(STYLE_WIDGET)

v1=QVBoxLayout()
brmAddButton(v1,"Stock",brmStock)
v1.addStretch(1)
brmAddButton(v1,"Users",brmUsers)

v2=QVBoxLayout()
v2.addStretch(1)
brmAddButton(v2,"Receipt",brmReceipt)
v2.addStretch(1)

v3=QVBoxLayout()
brmAddButton(v3,"Transfer",brmTransfer)
v3.addStretch(1)
brmAddButton(v3,"Donation",brmDonate)

bbox=QHBoxLayout()
bbox.addStretch(1)
bbox.addLayout(v1)
bbox.addStretch(1)
bbox.addLayout(v2)
bbox.addStretch(1)
bbox.addLayout(v3)
bbox.addStretch(1)

msgbox=QHBoxLayout()
msgbox.addStretch(1)
msg.setStyleSheet(STYLE_MSG)
msgbox.addWidget(msg)
msgbox.addStretch(1)

hbox=QHBoxLayout()
hbox.addStretch(1)
hlp=QLabel("Buy item by scanning its barcode\n\n"
	"Read the buttons and gues what they do :)")
hlp.setStyleSheet(STYLE_HELP)
hbox.addWidget(hlp)
hbox.addStretch(1)

screenbox=QVBoxLayout()
brmLabelBox(screenbox,"Welcome in BrmBar!")
screenbox.addLayout(msgbox)
screenbox.addStretch(1)
screenbox.addLayout(hbox)
screenbox.addStretch(3)
screenbox.addLayout(bbox)
screenbox.addStretch(1)
brmAddLine(screenbox,"",'T',STYLE_LE,brmBuy,c=1,foc=1)

mainWidget.setLayout(screenbox)
mainWidget.showFullScreen()

app.exec_()
