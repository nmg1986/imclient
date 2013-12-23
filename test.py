#!/usr/bin/env python2.7
#  vimejjfileencoding:utf8

from twisted.internet import protocol, reactor
from twisted.protocols.basic import Int32StringReceiver
from msg import MsgFactory

HOST = '10.5.1.114'
PORT = 6800 
import time
from struct import pack
import struct

import json
from struct import unpack

from mainPanel import MainPanel
from login import Login

class Client(Int32StringReceiver):
    def connectionMade(self):
        print("connect with server %s") % self.transport.getPeer().host	
        msg='{"Type":"REGISTER","OwnGuid":"custom-00000"}'
        self.sendString(msg)
        msg='{"Type":"GET_CUSTOM_GROUPS"}'
        print("Sending get-custom-groups msg...")
        self.sendString(msg)
        print("Done")
        
    #def stringReceived(self, msg):
    #    print("Recv msg : {}".format(msg))
    def dataReceived(self,msg):
        #print msg
        pass

    def lengthLimitExceeded(self,length):
        print length
        reactor.stop()
	
class ClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.msg=MsgFactory()
    def buildProtocol(self,addr):
        protocol=Client()
        protocol.factory=self
        protocol.msg=self.msg
        return protocol
    def clientConnectionLost(self,connector,reason):  
    	print 'connection lost'
        print reason
    	#reactor.stop()
    def clientConnectionFailed(self,connector,reason):
    	print 'connection failed'
    	reactor.stop()

reactor.connectTCP(HOST, PORT, ClientFactory())
reactor.run()
