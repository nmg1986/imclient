#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gtk
import time

from layout import LayOut


class MsgWindow(gtk.Window):
    def __init__(self,client,uid,name):
        gtk.Window.__init__(self)

	self.client=client
	self.uid=uid
	self.current_name='牛敏国'
	self.set_size_request(545,512)
	self.set_decorated(False)
	self.connect('key-press-event',self.sendMsg)
	
        self.vbox=gtk.VBox()
        self.add(self.vbox)
        
        self.titleBar=LayOut(self)
        self.vbox.pack_start(self.titleBar,False,False)
        
	vpaned=gtk.VPaned()
	self.vbox.pack_start(vpaned,False,False)

	scrolledwindow=gtk.ScrolledWindow()
	scrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
	scrolledwindow.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
	vpaned.add1(scrolledwindow)

	self.msgView=gtk.TextView()
	self.msgView.set_size_request(-1,300)
	self.msgView.set_editable(False)
	scrolledwindow.add(self.msgView)

	self.sendView=gtk.TextView()
	self.sendView.set_size_request(-1,300)
	vpaned.add2(self.sendView)

	self.bottomBar=LayOut(self)
	self.bottomBar.setHeight(40)
	self.vbox.pack_end(self.bottomBar,False,False)
	

    def run(self):
        self.show_all()

    def insertHead(self,color):
	   self.msgView.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))
	   view_buffer=self.msgView.get_buffer()
	   end=view_buffer.get_end_iter()
	   localtime=time.localtime()
	   current_time='{}:{}:{}'.format(localtime[3],localtime[4],localtime[5])
	   view_buffer.insert(end,self.current_name + ' ' + current_time + '\n') 
    def insertContent(self,text):
	   self.msgView.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
	   view_buffer=self.msgView.get_buffer()
	   end=view_buffer.get_end_iter()
	   view_buffer.insert(end,'\t ' + text + '\n') 
	   self.msgView.scroll_to_mark(view_buffer.get_insert(),0)
    def _sendMsg(self,text):
	   Type='CHAT'
	   Body=text
	   Created=int(time.time())
	   SendGuid=self.client.uid
	   RecvGuid=self.uid
	   msg=self.client.msg.packMsg(Type,Body,Created,SendGuid,RecvGuid)
	   self.client.transport.write(msg)


    def sendMsg(self,widget,event):
    	if event.keyval == 65293 :
	   _buffer=self.sendView.get_buffer()
	   text=_buffer.get_text(_buffer.get_start_iter(),_buffer.get_end_iter(),include_hidden_chars=False)
	   _buffer.delete(_buffer.get_start_iter(),_buffer.get_end_iter())
           self.insertHead('blue')
           self.insertContent(text)
           self._sendMsg(text)
	   return True
	return False
    def recvMsg(self,sender,msg,sendtime):
        if sender == 'custom-00001':
            sender="胡咺晖"
        elif sender == 'custom-00003':
            sender="黄艳英"
        elif sender == 'custom-00002':
            sender="聂桂莹"
        self.insertHead('blue') 
        self.insertContent(msg)
	  # self.msgView.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('blue'))
	  # view_buffer=self.msgView.get_buffer()
	  # end=view_buffer.get_end_iter()
	  # localtime=time.localtime()
	  # current_time='{}:{}:{}'.format(localtime[3],localtime[4],localtime[5])
	  # view_buffer.insert(end,sender + ' ' + current_time + '\n' + '\t' + msg + ' ' + '\n')
	  # self.msgView.scroll_to_mark(view_buffer.get_insert(),0)
    	

