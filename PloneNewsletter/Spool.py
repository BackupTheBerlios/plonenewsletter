# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

""" 
Spool for newsletter. Store e-mail requests and users pending for subscription.

$Id: Spool.py,v 1.1 2002/11/05 11:26:41 terraces Exp $
 """

import whrandom
import User
import re

from Globals import Persistent, InitializeClass

class Spool(Persistent):

    ## request types, associated to text to parse in mail subjects
    SUB = 'subscribe'
    UNSUB = 'unsubscribe'
    
    def __init__(self):
        """ Create spool instance """
        self.users = {} 
        self.requests = {}

###########################################
## Methods called by Newsletter instance ##
###########################################
               
    def addSubscription(self, user):
        """ Create a request to store user subscription request """
        self.users[user.email] = user
        self._p_changed = 1
        return self.addRequest(user.email, self.SUB)
        
    def checkSubscription(self, subject):
        """ Confirm subscription. Parse the subject to find revelant 
            informations and look for user in requests spool. 
            Then return requested user """
        email, id = self.parseSubject(subject)
        for rq in self.requests.values():
            if rq.request == self.SUB and rq.id == id and rq.email == email:
                user = self.users[email]
                del self.users[email], self.requests[id]
                self._p_changed = 1
                return user
        return None

    def addUnsubscription(self, user):
        """ add unsubscription request in requests spool """
        return self.addRequest(user.email, self.UNSUB)
    
    def checkUnsubscription(self, subject):
        """ Confirm unsubscription. Parse the subject to find revelant 
            informations and look for it in requests spool. 
            If exists, remove it from spool and returns removed user address """
        email, id = self.parseSubject(subject) 
        for rq in self.requests.values():
            if rq.request == self.UNSUB and rq.id == id and rq.email == email:
                del self.requests[id]
                self._p_changed = 1
                return email
        return None


######################################################
## Internal Methods, not called by Newsletter class ##
######################################################


    def addRequest(self, email, request):
        """ Add a request in spool """
        request = SpoolRequest(email, request)
        id = request.id
        self.requests[id]=request
        self._p_changed = 1
        return id 

    def parseSubject(self, subject):
        """ Get email and id from subject """
        s = subject.split()
        email = s[s.index('user:')+1]
        id = s[s.index('id:')+1] 
        return email, id
        
#################################
## Internal Class SpoolRequest ##
#################################
   
class SpoolRequest:

    """ Request """
       
    def __init__(self, email, request):
        """ class initialisation """
        ## TODO Trouver un id unique pour le dico ... !
        self.id = str(whrandom.random())[2:10]
        self.email = email
        self.request = request


InitializeClass(Spool)
InitializeClass(SpoolRequest)

