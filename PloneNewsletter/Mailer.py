# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
Mail functions of PloneNewsletter. Using MailHost for most operations.

$id$
"""

from User import User

from Acquisition import Explicit
from Globals import Persistent, InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
import string
import threading
from zLOG import LOG, WARNING, INFO, ERROR, DEBUG


class Mailer(Explicit, 
            Persistent):

    """ Mailer class """

    ## Acces to attributes
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess("allow")
    
    ## HTML or Txt format attributes, used in ZPT
    #HTM = 0
    #TXT = 1 
  
    def __init__(self, mailhost, mailFrom, nameFrom, signature):
        """ Instanciates class """
        self.mailhost = mailhost
        self.mailFrom = mailFrom
        self.nameFrom = nameFrom
        self.signature = signature

    def edit(self, mailFrom, nameFrom, signature):
        """ Change arttributes properties """
        self.mailFrom = mailFrom
        self.nameFrom = nameFrom
        self.signature = signature

#####################
## Sending methods ##
#####################

    def sendAll(self, publi, users, subject, message_txt, message_html):
        """ Send email to all newsletter members in a separate thread """
        mailthread = ThreadMailer(publi, self, users, subject, message_txt, message_html)
        mailthread.start()

    def sendValidate(self, to, subject, url):
        """ Send email to reviewers when publication submited """
        for i in to:        
            message = """ 
To:%s
From:%s
Return-path:%s
Content-type:text/plain; charset=iso-8859-1
Content-Transfer-Encoding: 8bit

A publication has been submited for reviewing.

You can validate it at the following URL:
%s""" %(i, self.getFrom(), self.getReturnPath(), url)
            self.mailhost.send(message, i, self.mailFrom, subject)

    def mailSubscribe(self, user, subject, message):
        """ Send e-mail to confirm subscription with specific 'from', in plain-text """
        mFrom = self.mailFrom.replace('@', '-list@')
        self.mailTo(user, subject, message, format='plain', mailFrom=mFrom)
        
    def mailUnsubscribe(self, user, subject, message):
        """ Send e-mail to confirm subscription with specific 'from', in plain-text """
        mFrom = self.mailFrom.replace('@', '-list@')
        self.mailTo(user, subject, message, format='plain', mailFrom=mFrom)

    def mailTo(self, user, subject, message, format='', mailFrom=''):
        """ Send the mail, adding headers first"""
        ## Content-type depends on user preferences, except for confirmation emails, in plain-text
        ## From equals self.from excepts for confirmation emails
        message = """ 
To:%s
From:%s
Return-path:%s
Content-type:text/%s; charset=iso-8859-1
Content-Transfer-Encoding: 8bit
%s""" %(user.getTo(), mailFrom or self.getFrom(), self.getReturnPath(), format or user.getFormat(), message)
        message = string.replace(message, '[your email]', user.email)
        message = self.addSign(message)
        self.mailhost.send(message, user.email, mailFrom or self.mailFrom, subject)

############################
## Other internal methods ##
############################
               
    def getFrom(self):
        """ Get a clean 'to' header with name and email """
        return """"%s" <%s>""" %(self.nameFrom, self.mailFrom)
     
    def addSign(self, message):
        """ Add signature to message """
        return self.signature=='' and message or """%s\n\n-- \n%s""" %(message, self.signature)
       
    def getReturnPath(self):
        """ Return path for error mails """
        return self.mailFrom.replace('@', '-error@')
        
####################
## Internal class ##
####################

class ThreadMailer(threading.Thread):

    """ Threaded mailer, used to send mail in a separated process """

    def __init__(self, publi, mailer, users, subject, message_txt, message_html):
        """ Instanciates class by running thread """
        ## thread properties
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 0.5
        self.publication = publi
        ## message properties
        self.mailer = mailer
        ### self.users = users
	### We must create new references, else we'll get into troubles with ZODB
	### when the main process dies
	self.users = {}
	for key in users.keys():
	    u = users[key]
	    self.users[key] = User(u.name[0], u.name[1], u.email, u.format)
        self.subject = subject
        self.message_txt = message_txt
        self.message_html = message_html

    def run(self):
        """ Threaded method: send mail to users """
	# List of users who have been sent the newsletter by this mailer
	self.publication.sent = ()
	self.publication.nbusers = len(self.users.keys())
        for user in self.users.values():
            ## send either html or plain text format according to user.format
            message = user.format and self.message_html or self.message_txt
            self.mailer.mailTo(user, self.subject, message)
            LOG('NewsServer', INFO, "ThreadMailer sent email to %s" % user.getTo())
	    self.publication.sent += (user,)
            self._finished.wait(self._interval)
        self.shutdown()

    def shutdown(self):
        """ Stop thread """
        self._finished.set()
                
InitializeClass(Mailer)
InitializeClass(ThreadMailer)


