#!/usr/bin/env python2.7
# -*- coding:utf8 -*-

import os
from twisted.internet.protocol import Factory,Protocol

if os.name != 'nt':
    #from twisted.internet import epollreactor
    #epollreactor.install()
    import mainloop
    mainloop.install()
else:
    from twisted.internet import iocpreactor
    iocpreactor.install()

from twisted.internet import reactor as mainloop

from twisted.internet.threads import deferToThread
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall

import time
from sys import stdout,exit
import signal
import struct

from buffer import MsgBuffer
from msg import MsgFactory
from mysql import MySql

from constant import ONLINE_MSG,OFFLINE_MSG

from threads import setOnLineMsg,setOffLineMsg,setSendFileMsg

import _mysql_exceptions

from log import logger

from constant import SERVER_PORT
import traceback

#PORT=6800
#import sys
#print sys.getdefaultencoding()

class Chat(Int32StringReceiver):
    def __init__(self):
        #self.msg=MsgFactory()

        self.login=False
        self.guid = None
        self.groups=None

        self.mysql=None
        self.msgHandle={
                'REGISTER'              	:   self.register,
                'UNREGISTER'            	:   self.unregister,
                'GET_CUSTOM_GROUPS'     	:   self.getGroups,
                'CREATE_CUSTOM_GROUP'   	:   self.addGroup,
                'DELETE_CUSTOM_GROUP'   	:   self.delGroup,
                'CHAT'                  	:   self.chat,
                'ADDUSER_CUSTOM_GROUP'  	:   self.addUser,
                'CUSTOM_USER_LOGIN'     	:   self.customLogin,
                'UPDATE_CUSTOM_GROUP'   	:   self.updateGroupName,
                'DELETEUSER_CUSTOM_GROUP' 	:   self.delUser,
                'FILE_TRANSFER_REQUEST' 	:   self.sendFile,
		'FILE_TRANSFER_CANCELLED'	:   self.sendFileCancel,
		'FILE_TRANSFER_ACCEPT'		:   self.sendFileAccept,
		'FILE_TRANSFER_REFUSED'		:   self.sendFileRefused,  
                'SHAKE_WINDOW'                  :   self.shakeWindow,
                'GET_USER_STATUS'       	:   self.getUserStatus,
		'CHANGE_PHOTO'			:   self.updatePhoto,
                }
    def connectionMade(self):
        logger.info("New connection from {!s}".format(self.getId()))
        self.mysql=MySql()
    def stringReceived(self,msg):
        logger.info("Received msg : {!s}".format(msg))
        msgType=self.msg.getValue(msg,'Type')
        msgHandler=self.msgHandle.get(msgType,self.errHandle)
        msgHandler(msg)
        #deferToThread(msgHandler,msg)
        #reactor.callInThread(msgHandler,msg)
        #self.sendString('hello,world')
    def register(self,msg):
        self.guid=self.msg.getValue(msg,'OwnGuid')
        ''' register user '''
        logger.info("Register user {!s}...".format(self.guid))
        self.factory.addClient(self.guid,self)
        logger.info("Done")
        if isinstance(self.mysql,MySql):
            ''' send online msg '''
            self.factory.sendNotify(self.guid,self.mysql,'ONLINE_NOTIFY')
            ''' check offline msg '''
            try:
                msgs=self.mysql.getOffLineMsg(self.guid)
            except _mysql_exceptions.ProgrammingError as error:
                logger.error(error)
		logger.error("{}".format(traceback.format_exc()))
                return
            if not msgs:
                logger.info("User {!s} has no offline msgs".format(self.guid))
            else:
                logger.info(msgs)
                for _msg in msgs:
                    arg=('OFFLINE_MSG',_msg[1],_msg[2],_msg[3],_msg[4])
                    message=self.msg.packMsg(*arg)
                    logger.info("Sending offline msgs : {!s}".format(message))
                    self.transport.write(message)
            ''' register in database '''
            self.mysql.setOnLineUser(self.guid)
            ''' send online msg '''
        else:
            ''' database init failed '''
            pass
    def unregister(self,msg):
	OwnGuid=self.msg.getValue(msg,'OwnGuid')
        logger.info("Unregister user {!s}...".format(self.guid))
        self.factory.delClient(self.guid)
        logger.info("Done")
        self.factory.sendNotify(self.guid,self.mysql,'OFFLINE_NOTIFY')
        self.mysql.delOnLineUser(self.guid)
    def getGroups(self,msg):
        def sendGroup():
            self.groups=self.mysql.getGroups(self.guid)
            if self.groups :
                for group in self.groups :
                    arg=('CUSTOM_GROUPS',group['gid'],group['gname'],group['users'],group['created'],group['weight'])
                    groupMsg=self.msg.packMsg(*arg)
                    logger.info("Sending group msg : {!s}".format(groupMsg))
                    self.transport.write(groupMsg)
            else:
                logger.info("{!s} has no custom groups,created them!".format(self.guid))
                try:
                    self.mysql.setDefaultGroups(self.guid)
                except Exception :#as error:
                    logger.error("Set default groups failed!!!")
		    #logger.error("{}".format(error))
		    #logger.error("{}".format(error.__doc__))
		    logger.error("{}".format(traceback.format_exc()))
                sendGroup()
            return
        logger.info("Sending group msgs begin...")
        sendGroup()
        logger.info("Sending group msgs end")
        return
    def getUserStatus(self,msg):
        Type=self.msg.getValue(msg,'Type') 
        #UserGuid=self.msg.getValue(msg,'UserGuid')
        GroupID=self.msg.getValue(msg,'GroupID')
        Users=self.mysql.getOnlineUser(GroupID)
        arg=(Type,GroupID,Users)
        msg=self.msg.packMsg(*arg)
        logger.info("Sending user status msg...")
        logger.info(msg)
        self.transport.write(msg)
    def delGroup(self,msg):
        #gid=self.msg.getValue(msg,'GroupID')
        #uid=self.msg.getValue(msg,'OwnGuid')
        GroupID=self.msg.getValue(msg,'GroupID')
        OwnGuid=self.msg.getValue(msg,'OwnGuid')
        if OwnGuid != self.guid:
            return
        logger.info("Delete group {!s}...".format(GroupID))
        try:
            self.mysql.delGroup(GroupID,OwnGuid)
        except Exception:
            logger.error("Delete group failed!!!")
	    logger.error("{}".format(traceback.format_exc()))
        logger.info("Done")
        arg=('DELETE_CUSTOM_GROUP',GroupID,OwnGuid)
        msg=self.msg.packMsg(*arg)
        logger.info("Send deleted group msg : {!s}".format(msg))
        self.transport.write(msg)
    def addGroup(self,msg):
        try:
            OwnGuid=self.msg.getValue(msg,'OwnGuid')
        except KeyError:
            logger.error("add group msg has no OwnGuid")
            return
        try:
            GroupName=self.msg.getValue(msg,'GroupName')
        except KeyError:
            logger.error("add group msg has no GroupName")
            return
        try:
            Weight=self.msg.getValue(msg,'Weight')
        except KeyError:
            logger.error("add group msg has no Weight")
            return
        try:
            GroupName=GroupName.encode('utf8')
            logger.info("Add group {!s}...".format(GroupName))
            pass
        except UnicodeDecodeError:
            pass
        try:
            self.mysql.addGroup(OwnGuid,GroupName,Weight)
            logger.info("Done")
        except _mysql_exceptions.IntegrityError as err:
            logger.error("Failed")
            logger.error("{!s}".format(err[1]))
        group=self.mysql.getGroups(OwnGuid,GroupName)[0]
        arg=('CREATE_CUSTOM_GROUP',group)
        groupMsg=self.msg.packMsg(*arg)
        logger.info("Send group msg : {!s}".format(groupMsg))
        self.transport.write(groupMsg)
    def updateGroupName(self,msg):
        GroupID=self.msg.getValue(msg,'GroupID')
        GroupName=self.msg.getValue(msg,'GroupName')
        OwnGuid=self.msg.getValue(msg,'OwnGuid')
        if OwnGuid != self.guid:
            return
        try:
            self.mysql.renameGroup(GroupID,GroupName)
        except :
            logger.error("Rename group failed!!!\n")
        arg=('UPDATE_CUSTOM_GROUP',GroupID,GroupName,OwnGuid)
        msg=self.msg.packMsg(*arg)
        logger.info("Sending rename group msg : {!s}".format(msg))
        self.transport.write(msg)
    def addUser(self,msg):
        GroupID=self.msg.getValue(msg,'GroupID')
        UserGuid=self.msg.getValue(msg,'UserGuid')
        Created=int(time.time())
        self.mysql.addUser(GroupID,UserGuid)
        arg=('ADDUSER_CUSTOM_GROUP',GroupID,UserGuid,Created)
        msg=self.msg.packMsg(*arg)
        logger.info("Sending add user msg : {!s}".format(msg))
        self.transport.write(msg)
    def delUser(self,msg):
        GroupID=self.msg.getValue(msg,'GroupID')
        OwnGuid=self.msg.getValue(msg,'OwnGuid')
        UserGuid=self.msg.getValue(msg,'UserGuid')
        if OwnGuid != self.guid:
            return 
        self.mysql.delUser(GroupID,UserGuid)
        logger.info("Delete user {!s} of group {!s}".format(UserGuid,GroupID))
        arg=('DELETEUSER_CUSTOM_GROUP',GroupID,OwnGuid,UserGuid)
        msg=self.msg.packMsg(*arg)
        logger.info("Sending delete user msg : {!s}".format(msg))
        self.transport.write(msg)
    def chat(self,msg):
        #if self.login :
            msgBody=self.msg.getValue(msg,'Body')
            msgCreated=int(time.time())
            msgRecvGuid=self.msg.getValue(msg,'RecvGuid')
            msgSendGuid=self.msg.getValue(msg,'SendGuid')
            blacklist=self.mysql.getBlackList(msgRecvGuid)
            if msgSendGuid not in blacklist:
                arg=('CHAT',msgBody,msgCreated,msgSendGuid,msgRecvGuid)
                msg=self.msg.packMsg(*arg)
                receiver=self.factory.getClient(msgRecvGuid)
                if not receiver:
                    logger.info("User {!s} if offline,write the msg to mysql".format(msgRecvGuid))
                    arg=('CHAT',msgBody,msgCreated,msgSendGuid,msgRecvGuid,self.mysql)
		    setOffLineMsg(*arg)
                    #T=setOffLineMsg(*arg)
                    #T.setDaemon(True)
                    #T.start()
                    return
                logger.info("Sending msgs to user {!s}".format(msgRecvGuid))
                receiver.transport.write(msg)
            else:
                logger.info("you are in receiver's blacklist,so sorry...")
            logger.info("Writing msgs to database...")
            arg=('CHAT',msgBody,msgCreated,msgSendGuid,msgRecvGuid,self.mysql)
	    setOnLineMsg(*arg)
            #T=setOnLineMsg(*arg)
            #T.setDaemon(True)
            #T.start()
        #else:
        #    stdout.write("[{!s}] you haven't login,sorry!!!\n".format(time.ctime()))
    def shakeWindow(self,msg):
        Type=self.msg.getValue(msg,'Type')
        RecvGuid=self.msg.getValue(msg,'RecvGuid')
        SendGuid=self.msg.getValue(msg,'SendGuid')
        msg=self.msg.packMsg(Type,RecvGuid,SendGuid)
        logger.info("Sending shake-window msg ...")
        logger.info(msg)
        self.factory.clients[RecvGuid].transport.write(msg)
    def sendFile(self,msg):
        RecvGuid=self.msg.getValue(msg,'RecvGuid')
        SendGuid=self.msg.getValue(msg,'SendGuid')
        Type=self.msg.getValue(msg,'Type')
        Created=self.msg.getValue(msg,'Created')
        DisplayName=self.msg.getValue(msg,'DisplayName')
        Length=self.msg.getValue(msg,'Length')
	NodeID=self.msg.getValue(msg,'NodeID')
	IP=self.getId()
        if RecvGuid in self.factory.clients:
            logger.info("User {!s} is online...".format(RecvGuid))
            arg=(Type,Created,DisplayName,RecvGuid,SendGuid,Length,NodeID,IP)
            msg=self.msg.packMsg(*arg)
            logger.info("Send send-file-msg to {!s}...".format(RecvGuid))
            logger.info("{!s}".format(msg))
            self.factory.clients[RecvGuid].transport.write(msg)
	    logger.info("Write send-file-msg to database...")
            arg=(Type,Created,DisplayName,RecvGuid,SendGuid,Length,NodeID,IP,self.mysql)
	    setSendFileMsg(*arg)
	    logger.info("Done")
        else:
            logger.info("User {!s} is offline...".format(RecvGuid))
            logger.info("Give it to me...")
    def sendFileCancel(self,msg):
	'''
	{"Type":"FILE_TRANSFER_CANCELLED","NodeID":0,"RecvGuid":"custom-00001"} '''
	Type=self.msg.getValue(msg,'Type')
	NodeID=self.msg.getValue(msg,'NodeID')
	RecvGuid=self.msg.getValue(msg,'RecvGuid')
	ActionCode=self.msg.getValue(msg,'ActionCode')
	arg=(Type,NodeID,ActionCode)
	msg=self.msg.packMsg(*arg)
	logger.info("Send send-file-cancel msg...")
	logger.info(msg)
	if RecvGuid in self.factory.clients:
		self.factory.clients[RecvGuid].transport.write(msg)
	else:
		logger.info("User {} is offline!".format(RecvGuid))
    def sendFileAccept(self,msg):
	Type=self.msg.getValue(msg,'Type')
	NodeID=self.msg.getValue(msg,'NodeID')
	RecvGuid=self.msg.getValue(msg,'RecvGuid')
	arg=(Type,NodeID)
	msg=self.msg.packMsg(*arg)
	logger.info("Send send-file-accept msg...")
	logger.info(msg)
	if RecvGuid in self.factory.clients:
		self.factory.clients[RecvGuid].transport.write(msg)
	else:
		logger.info("User {} is offline!".format(RecvGuid))
	
    def sendFileRefused(self,msg):
	pass
    def updatePhoto(self,msg):
	OwnGuid=self.msg.getValue(msg,'OwnGuid')
	Photo=self.msg.getValue(msg,'Photo')
	self.mysql.updatePhoto(OwnGuid,Photo)
    def customLogin(self,msg):
        logger.info("Recv login msg : {!s}".format(msg))
        UserName=self.msg.getValue(msg,'UserName')
        PassWord=self.msg.getValue(msg,'PassWord')
        SerialNumber=self.msg.getValue(msg,'SerialNumber')
        try:
            UserInfo=self.mysql.getUserInfo(UserName)
        except _mysql_exceptions.OperationalError as err:
            logger.error(err)
        if not UserInfo :
            UserID=-1   # no uid
            ErrorCode=1 # no such user
            DisplayName=''
            arg=('CUSTOM_USER_LOGIN',UserID,ErrorCode,SerialNumber,DisplayName)
            msg=self.msg.packMsg(*arg)
            logger.warning("No such user,check please!!!")
            logger.info("Sending login msg : {!s}".format(msg))
            self.transport.write(msg)
            return
        __password=UserInfo[1]
        if PassWord != __password :
            UserID=-1   # can not get uid
            ErrorCode=2 # password does not match
            DisplayName=''
            arg=('CUSTOM_USER_LOGIN',UserID,ErrorCode,SerialNumber,DisplayName)
            msg=self.msg.packMsg(*arg)
            logger.warning("Password does not match!!!")
            logger.info("Sending login msg : {!s}".format(msg))
            self.transport.write(msg)
            return
        UserID=UserInfo[0] # real user id
        ErrorCode=0         # 0 means check pass 
        DisplayName=UserInfo[2]
        arg=('CUSTOM_USER_LOGIN',UserID,ErrorCode,SerialNumber,DisplayName)
        msg=self.msg.packMsg(*arg)
        logger.info("Login succeed,congratulations!")
        logger.info("Sending login msg : {!s}".format(msg))
        self.transport.write(msg)
        self.login=True

	
    def errHandle(self,msg):
        pass

    def connectionLost(self, reason):
        logger.info("Connection lost from {!s}".format(self.getId()))
        self.factory.delClient(self.guid)
        self.factory.sendNotify(self.guid,self.mysql,'OFFLINE_NOTIFY')
        logger.info("Shutdown database connection")
        self.mysql.delOnLineUser(self.guid)
        self.mysql.close()

    def getId(self):
        return str(self.transport.getPeer().host)

class ChatFactory(Factory):
    def __init__(self):
        self.clients = {}
        self.loopcall=LoopingCall(self.getOnLineUser)
        self.loopcall.start(60,False)
        self.msg=MsgFactory()
    def buildProtocol(self,addr):
        protocol=Chat()
        protocol.factory=self
        protocol.msg=self.msg
        return protocol
    def addClient(self,*newclient):
        self.clients[newclient[0]]=newclient[1]

    def delClient(self,client):
        if self.clients.has_key(client):
            self.clients.pop(client)
    def getClient(self,guid):
        return self.clients.get(guid,None)

    def sendAll(self, message):
        for proto in self.clients:
            proto.transport.write(message + "\n")
    def sendNotify(self,guid,mysql,notify):
        ''' users is a generator object ''' 
        users=mysql.getUsers(guid)
        for user in users:
           if user in self.clients:
               if user != guid:
                    logger.info("Sending {!s}...{!s}".format(notify,user))
                    msg=self.msg.packMsg(notify,guid)
                    logger.info("Sending {!s} msg : {!s}".format(notify,msg))
                    self.clients[user].transport.write(msg)
		    #print user
    def getOnLineUser(self):
        user=len(self.clients)
        logger.info("Online user num is {}".format(user))


if __name__ == '__main__':
    mainloop.listenTCP(SERVER_PORT,ChatFactory())
    logger.info("Start HBIM Server...")
    logger.info("Listen on *:{!s}".format(SERVER_PORT))
    logger.info("Waiting for connections...")
    mainloop.initDaemon()
    mainloop.run()
else:
    from twisted.application import internet,service
    application=service.Application("HBIMServer")
    service=internet.TCPServer(SERVER_PORT,ChatFactory())
    service.setServiceParent(application)
    logger.info("Start HBIM Server...")
    logger.info("Listen on *:{!s}".format(SERVER_PORT))
    logger.info("Waiting for connections...")
