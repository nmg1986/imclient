# -*- coding:utf8 -*-

from struct import pack,unpack
import json
from custom import doubleQuoteDict
import time
from constant import MSG_HEAD_LEN

class MsgFactory(object):
    def __init__(self):
        self.handler={
			'REGISTER'		:   self.register,
			'GET_CUSTOM_GROUPS'	:   self.getCustomGroups,
                        'CUSTOM_GROUPS'         :   self.getGroups,
                        'CHAT'                  :   self.ChatMsg,
                        'OFFLINE_MSG'           :   self.OffLineMsg,
                        'ONLINE_NOTIFY'         :   self.OnLineNotify,
                        'OFFLINE_NOTIFY'        :   self.OffLineNotify,
                        'ADDUSER_CUSTOM_GROUP'  :   self.addUser,
                        'DELETEUSER_CUSTOM_GROUP' : self.delUser,
                        'DELETE_CUSTOM_GROUP'   :   self.delGroup,
                        'CREATE_CUSTOM_GROUP'   :   self.addGroup,
                        'CUSTOM_USER_LOGIN'     :   self.customUser,
                        'UPDATE_CUSTOM_GROUP'   :   self.rnGroup,
                        'FILE_TRANSFER_REQUEST' :   self.sendFile,
			'FILE_TRANSFER_CANCELLED':  self.sendFileCancelled,
                        'GET_USER_STATUS'       :   self.userStatus,
                        'SHAKE_WINDOW'          :   self.shakeWindow,
                     }
    def getValue(self,msg,obj):
        value=json.loads(msg)[obj]
        return value
    def packMsg(self,*args):
        msg=self.handler[args[0]](*args)
        return msg
    def formatMsg(self,msg):
        msg=doubleQuoteDict(msg)
        msgLen=len(str(msg))	
        msg=pack("!i%ds" % msgLen,msgLen,str(msg))
        return msg
    def register(self,*args):
    	msg={}
	msg['Type']=args[0]
	msg['OwnGuid']=args[1]
        msg=self.formatMsg(msg)
        return msg
    def getCustomGroups(self,*args):
    	msg={}
	msg['Type']='GET_CUSTOM_GROUPS'
	msg=self.formatMsg(msg)
	return msg
    def getGroups(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['GroupName']=args[2]
        msg['Users']=args[3]
        msg['Created']=args[4]
        msg['Weight']=args[5]
        msg=self.formatMsg(msg)
        return msg
    def userStatus(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['Users']=args[2]
        msg=self.formatMsg(msg)
        return msg
    def ChatMsg(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['Body']=args[1]
        msg['Created']=args[2]
        msg['SendGuid']=args[3]
        msg['RecvGuid']=args[4]
        msg=self.formatMsg(msg)
        return msg

    def OffLineMsg(self,*args):
        msg={}
        msg['Type']='CHAT'
        msg['Body']=args[1]
        msg['Created']=args[2]
        msg['SendGuid']=args[3]
        msg['RecvGuid']=args[4]
        msg=self.formatMsg(msg)
        return msg
    def addUser(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['UserGuid']=args[2]
        msg['Created']=args[3]
        msg=self.formatMsg(msg)
        return msg
    def delUser(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['OwnGuid']=args[2]
        msg['UserGuid']=args[3]
        msg=self.formatMsg(msg)
        return msg
    def addGroup(self,*args):
        msg={}
        msg['Type']='CUSTOM_GROUPS'
        msg['GroupID']=args[1]['gid']
        msg['GroupName']=args[1]['gname']
        msg['Users']=args[1]['users']
        msg['Created']=args[1]['created']
        msg['Weight']=args[1]['weight']
        msg=self.formatMsg(msg)
        return msg
    def rnGroup(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['GroupName']=args[2]
        msg['OwnGuid']=args[3]
        msg=self.formatMsg(msg)
        return msg
    def sendFile(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['Created']=args[1]
        msg['DisplayName']=args[2]
        msg['RecvGuid']=args[3]
        msg['SendGuid']=args[4]
        msg['Length']=args[5]
	msg['NodeID']=args[6]
	msg['IP']=args[7]
        msg=self.formatMsg(msg)
        return msg
    def sendFileCancelled(self,*args):
	msg={}
	msg['Type']=args[0]
	msg['NodeID']=args[1]
	msg['ActionCode']=args[2]
	msg=self.formatMsg(msg)
	return msg
    def delGroup(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['GroupID']=args[1]
        msg['OwnGuid']=args[2]
        msg=self.formatMsg(msg)
        return msg
    def customUser(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['UserName']=args[1]
        msg['PassWord']=args[2]
        msg['SerialNumber']=args[3]
        msg=self.formatMsg(msg)
        return msg
    def OnLineNotify(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['Guid']=args[1]
        msg=self.formatMsg(msg)
        return msg
    def OffLineNotify(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['Guid']=args[1]
        msg=self.formatMsg(msg)
        return msg
    def shakeWindow(self,*args):
        msg={}
        msg['Type']=args[0]
        msg['RecvGuid']=args[1]
        msg['SendGuid']=args[2]
        msg=self.formatMsg(msg)
        return msg
