import gtk

class LayOut(gtk.Layout):
    def __init__(self,parent):
        gtk.Layout.__init__(self)

        self.begin_x=''
        self.begin_y=''
        self.end_x=''
        self.end_y=''
        self.motion=False
        self._parent=parent
        self.set_size_request(-1, 100)
        self.connect('button-press-event',self.mouse_press)
        self.connect('button-release-event',self.mouse_release)
        self.connect('motion-notify-event',self.mouse_motion)
        self.connect('expose-event',self.draw_pixbuf)
        self.set_events( gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)

    def mouse_press(self,widget,event):
        if event.button == 1:
            if not self.motion:
                self.motion = True
                self.begin_x, self.begin_y = event.x, event.y

    def mouse_release(self,widget,event):
        self.motion = False

    def mouse_motion(self,widget,event):
        if self.motion :
            self.end_x, self.end_y = event.x_root, event.y_root
            self._parent.move(int(self.end_x - self.begin_x),
                    int(self.end_y - self.begin_y))

    def draw_pixbuf(self,widget,event):
        path = 'img/bg.jpg'
        rec=widget.get_allocation()
        width,height=rec.width,rec.height
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path,10000,10000)
        widget.bin_window.draw_pixbuf(widget.style.bg_gc[gtk.STATE_NORMAL],
                pixbuf, 0, 0, 0,0)
    def setHeight(self,height):
        self.set_size_request(-1,height)
