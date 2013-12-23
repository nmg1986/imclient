#!/usr/bin/env python
# -*-coding:utf-8-*-

import gtk
from hashlib import md5
from client import ClientFactory
from msg    import MsgFactory
from layout import LayOut

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import protocol, reactor

HOST='10.5.1.114'
PORT=6800

class Login(gtk.Window):
    def __init__(self):
    	gtk.Window.__init__(self)

        self.msg=MsgFactory()	

	self.set_default_size(400,200)
	self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
	self.set_keep_above(True)
	self.set_decorated(False)
	self.connect('key-press-event',self.login)
	self.layout=LayOut(self)
	self.add(self.layout)

	#self.fix=gtk.Fixed()
	#self.fix.set_size_request(400,100)
	#self.layout.put(self.fix,0,50)

	label=gtk.Label("用户名")
	self.layout.put(label,100,55)
	self.username=gtk.Entry()
	self.username.set_has_frame(False)
	self.username.grab_focus()
	self.username.set_size_request(150,25)
	self.layout.put(self.username,150,50)

	label=gtk.Label("密 码")
	self.layout.put(label,100,105)
	self.password=gtk.Entry()
	self.password.set_has_frame(False)
	self.password.set_size_request(150,25)
	self.layout.put(self.password,150,100)

    def run(self):
    	self.show_all()
        self.connector=reactor.connectTCP(HOST,PORT,ClientFactory(self))
        self.transport=self.connector.transport
        reactor.run()
    def login(self,widget,event):
    	if event.keyval == 65293:
	   username=self.username.get_text()
	   password=self.password.get_text()
           self.sendLoginMsg(username,password)
        if event.keyval == 65307:
            self.destroy()
            gtk.main_quit()
    def sendLoginMsg(self,username,password):
           Type='CUSTOM_USER_LOGIN'
           PassWord=md5(password).hexdigest()
           UserName=username
           SerialNumber=0
           msg=self.msg.packMsg(Type,UserName,PassWord,SerialNumber)
           print("Sending login-msg ...")
           self.transport.write(msg)
           print("Done")
           for child in self.layout.get_children():
                self.layout.remove(child)
login=Login()
login.run()
