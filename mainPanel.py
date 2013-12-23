#!/usr/bin/env python
# -*-coding:utf-8-*-

import gtk
from msgWindow import MsgWindow
from layout import LayOut

class MainPanel(gtk.Window):
	def __init__(self,client):
    	    gtk.Window.__init__(self)

	    self.user_map={}
	    self.client=client

	    self.set_keep_above(True)
	    self.set_position(gtk.WIN_POS_CENTER)
	    self.set_decorated(False)
	    self.set_size_request(277,597)
	    self.set_resizable(False)
	    self.connect('key-press-event',self.logout)

	    #self.fix=gtk.Fixed() 
	    #self.add(self.fix)
	    self.layout=LayOut(self)
	    self.add(self.layout)

            self.userView=self.create_user_view()
            self.userModel=self.create_user_model()
            self.userView.set_model(self.userModel)
	    self.layout.put(self.userView,0,100)

            #control_button=self.create_control_button()
            #self.fix.put(control_button,0,560)

	    #search=gtk.Entry()
	    #search.set_size_request(277,30)
	    #search.set_has_frame(False)
	    ##fix.put(search,0,80)

            #iconview=gtk.IconView()
            #iconview.set_size_request(277,35)
            #iconview.set_column_spacing(0)
            #iconview.set_row_spacing(0)
            #iconview.set_item_width(92)
            #iconview.set_text_column(0)
            #iconview.set_margin(0)
            #iconview.set_border_width(0)
            ##iconview.set_item_padding(35)
            #self.fix.put(iconview,0,70)
            #iconview.connect('selection-changed',self.selection_changed)

            ##print gtk.treepath_new_from_string("0")
            ##path=iconview.get_path_at_pos(0,0)
            ##iconview.select_path((0,))
            #iconview.item_activated((0,))

            ##style=iconview.get_style().copy()
            ##style_fix=self.get_style()
            ##for state in ( gtk.STATE_NORMAL,gtk.STATE_PRELIGHT,gtk.STATE_ACTIVE):
            ##    style.base[state]=style_fix.bg[gtk.STATE_NORMAL]
            ##iconview.set_style(style)

            #model=gtk.ListStore(str)
            #iconview.set_model(model)
            #model.append(['我的好友'])
            #model.append(['最近联系人'])
            #model.append(['群和讨论组'])
        def create_user_view(self):
	    treeview=gtk.TreeView()
            treeview.set_rules_hint(True)
	    treeview.set_headers_visible(False)
	    treeview.connect('row-activated', self.chat_window)
            treeview.set_size_request(277,450)

	    rendererText=gtk.CellRendererText()
	    rendererText.set_fixed_size(-1,30)
	    column=gtk.TreeViewColumn("",rendererText,text=0)
	    treeview.append_column(column)

	    rendererText=gtk.CellRendererText()
	    column=gtk.TreeViewColumn("",rendererText,text=1)
	    column.set_visible(False)
	    treeview.append_column(column)
            
            return treeview
        def create_user_model(self):
	    treestore=gtk.TreeStore(str,str)
            return treestore

        def create_control_button(self):
            button=gtk.Button("退出")
            button.connect("clicked",gtk.main_quit)
            return button

        def logout(self,widget,event):
    	    if event.keyval == 65307:
	    	self.destroy()
		gtk.main_quit()
	
	def update(self,gname,users):
	    parent=self.userModel.append(None,[gname,''])
	    if not users:
	    	self.userModel.append(parent,['',''])
	    else:
	    	for user in users:
	    	    self.userModel.append(parent,[user[0],user[1]])
	def chat_window(self, treeview, path, column):
	    model=treeview.get_model()
	    treeiter=model.get_iter(path)
	    name=model.get_value(treeiter,0)
	    uid=model.get_value(treeiter,1)
	    msgWindow=MsgWindow(self.client,uid,name)
	    msgWindow.run()
	    self.user_map[uid]=msgWindow

	def run(self):
	    self.show_all()
