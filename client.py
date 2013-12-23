#!/usr/bin/env python2.7
#  vimejjfileencoding:utf8

from twisted.internet import protocol
from twisted.protocols.basic import Int32StringReceiver
from msg import MsgFactory


from mainPanel import MainPanel

class Client(Int32StringReceiver):
    def __init__(self):
	self.mainPanel=None
	self.uid=None
	self.msgHandler={
                'CHAT'                  	:   self.chatMsg,
                'CUSTOM_USER_LOGIN'     	:   self.customLogin,
		'CUSTOM_GROUPS'			:   self.customGroups,
        }

    def customLogin(self,msg):
        print("Recv login response ...")
        print(msg)
    	ErrorCode=self.msg.getValue(msg,'ErrorCode')
	UserID=self.msg.getValue(msg,'UserID')
	self.uid=UserID
	if ErrorCode == 0 :
            self.factory.loginWindow.destroy()
	    self.register(self.uid)
    def register(self,uid):
    	msg=self.msg.packMsg('REGISTER',uid)
        print("Sending register msg...")
	self.transport.write(msg)
        print("Done")
	self.mainPanel=MainPanel(self)
	self.mainPanel.run()
	if isinstance(self.mainPanel,MainPanel):
	    self.getCustomGroups()
    def getCustomGroups(self):
    	msg=self.msg.packMsg('GET_CUSTOM_GROUPS')
        print("Sending get-custom-groups msg...")
	self.transport.write(msg)
        print("Done")
    def customGroups(self,msg):
    	GroupName=self.msg.getValue(msg,'GroupName')
	Users=self.msg.getValue(msg,'Users')
	user_list=list()
	if Users is not None:
	    for user in Users:
	        uname=user['DisplayName']
	        uid=user['UserGuid']
	        user_list.append((uname,uid))
	    print GroupName,user_list
	if isinstance(self.mainPanel,MainPanel):
	    self.mainPanel.update(GroupName,user_list)
	else:
            pass
    def chatMsg(self,msg):
    	RecvUid=self.msg.getValue(msg,'RecvGuid')
	SendUid=self.msg.getValue(msg,'SendGuid')
	SendTime=self.msg.getValue(msg,'Created')
	MsgContent=self.msg.getValue(msg,'Body')
        print msg
        #try:
	#    self.mainPanel.user_map[SendUid].recvMsg(SendUid,MsgContent,SendTime)
        #except KeyError:
        #    print 'users window is not open...'
    def errHandle(self,msg):
        print msg
    def lengthLimitExceeded(self,length):
        print length
        return
    def connectionMade(self):
        print("connect with server %s") % self.transport.getPeer().host	
    def stringReceived(self, msg):
        msgType=self.msg.getValue(msg,'Type')
        msgHandler=self.msgHandler.get(msgType,self.errHandle)
        msgHandler(msg)
        return 
	
class ClientFactory(protocol.ClientFactory):
    def __init__(self,loginWindow):
        self.msg=MsgFactory()
        self.loginWindow=loginWindow
    def buildProtocol(self,addr):
        protocol=Client()
        protocol.factory=self
        protocol.msg=self.msg
        return protocol
    def clientConnectionLost(self,connector,reason):  
    	print 'connection lost'
    	reactor.stop()
    def clientConnectionFailed(self,connector,reason):
    	print 'connection failed'
    	reactor.stop()

