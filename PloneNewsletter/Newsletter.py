# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
Advanced Newsletter system for Plone.
The newsletter is created for a bunch of articles stored in a folder.
Users can subscribe/unsubscribe to the mailing list, with confirmation e-mail.

$Id: Newsletter.py,v 1.1 2002/11/05 11:26:40 terraces Exp $
"""

## ZOPE imports
from AccessControl import ClassSecurityInfo
from Globals import Persistent, InitializeClass
from Acquisition import aq_base

##  CMF imports
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName


from DateTime import DateTime

#
import re
import whrandom
from User import User
from Spool import Spool
from Mailer import Mailer
import string

######################################
## Newslette properties and methods ##
######################################

factory_type_information = (
    {'id'                   : 'Newsletter',
    'meta_type'             : 'Newsletter',
    'description'           : ('Advanced Newsletter; the newsletter is automatically composed from a bunch of articles.'),
    'icon'                  : 'newsletter_icon.png',
    'product'               : 'PloneNewsletter',
    'factory'               : 'addNewsletter',
    'immediate_view'        : 'folder_contents',
    'filter_content_types'  : 1,
    'allowed_content_types' : ('Publication','Folder'),
    'actions'       : (
        {'id'           : 'view',
         'name'         : 'View',
         'action'       : 'folder_listing',
         'permissions'  : (CMFCorePermissions.View,),
         'category'	    : 'folder',			
        },
        {'id'           : 'edit',
         'name'         : 'Edit',
         'action'       : 'portal_form/newsletter_edit_form',
         'permissions'  : (CMFCorePermissions.ModifyPortalContent,),
         'category'     : 'folder',
        },
        {'id'           : 'users',
         'name'         : 'Users',
         'action'       : 'users_view',
         'permissions'  : (CMFCorePermissions.ModifyPortalContent,),
         'category'     : 'folder',
        },
        {'id'           : 'localroles'
        , 'name'        : 'Local Roles'
	    , 'action'      : 'folder_localrole_form'
	    , 'permissions' : (CMFCorePermissions.ManageProperties,)
	    , 'category'    : 'folder'
        },
        ),
    }
)

def addNewsletter(self, 
        id, 
        title='',
        description='',
		topics='',
        mailFrom='',
        nameFrom='',
        mailReply='',
		disclaimer='',
        signature='',
        ):
				
    """ Create an empty Newsletter """
    newsletter_object = Newsletter(id, title, description, topics, mailFrom, nameFrom, disclaimer, signature)
    self._setObject(id, newsletter_object)


class Newsletter(PortalFolder,
        PortalContent,
        DefaultDublinCoreImpl,
        ):
	
    """ Plone NewsLetter Class """

    meta_type = 'Newsletter'
    portal_type = 'PloneNewsLetter'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    ## subscribe and ubsubscribe expressions
    SUB = 'Subscription'
    UNSUB = 'Unsubscription'
    MOD = 'Modify'

    def __init__(self, 
            id, 
            title='',
            description='',
            topics='',
            mailFrom='',
            nameFrom='',
            disclaimer='',
            signature='',
            ):

        """ Initialize an instance of the class """		
        ## parents constructors 
        DefaultDublinCoreImpl.__init__(self, title, description = description)
        self.id = id
        self.topics = string.split(topics,'\n')
        self.disclaimer = disclaimer		
        self.mailer = Mailer(None, mailFrom, nameFrom, signature)
        self.spool = Spool()
        self.users = {}

    def edit(self,
        title,
        description='',
        topics='',
        mailFrom='',
        nameFrom='',
        disclaimer='',
        signature='',
        ):

        """ Edit Newsletter Properties """
        self.editMetadata(title = title, description = description)
        self.topics = string.split(topics,'\n')
        self.disclaimer = disclaimer
        self.mailer.edit(mailFrom, nameFrom, signature)
        ## edit mailhost aswe can't do it in  __init__()
        if self.mailer.mailhost is None:
            self.mailer.mailhost = self.getMailHost()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
         """ Add self to the workflow and catalog. """
         PortalFolder.manage_afterAdd(self, item, container)
         PortalContent.manage_afterAdd(self, item, container)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        """ Remove self from the workflow and catalog. """
    	if aq_base(container) is not aq_base(self):
            self.unindexObject()
        PortalFolder.manage_beforeDelete(self, item, container)

#    security.declareProtected(CMFCorePermissions.View, 'view')
#    def view(self, REQUEST):
#        """ List the contents og the newsletter """
#        return self.newsletter_view(self, REQUEST)

    security.declareProtected(CMFCorePermissions.AddPortalContent, 'invokeFactory')
    def invokeFactory( self
            , type_name
            , id
            , RESPONSE=None
            , *args
            , **kw
            ):

        """ Invokes the portal_types tool. """		
        pt = getToolByName( self, 'portal_types' )
        apply( pt.constructContent
            , (type_name, self, id, RESPONSE) + args
            , kw
        )

    def mailerAttr(self, attribute=None) :        
        """ Returns an attribute of mailer, as can't call mailer.attr in ZPT """ 
        return eval('self.mailer.%s' %attribute)

######################################
## User subscription/unsubscription ##
######################################

    def subscribe(
        self,
        firstName='',
        lastName='',
        email='',
        format='',
        ):

        """ User subscription """        
        if email in self.users.keys():
            return 0
        else:
            user = User(firstName, lastName, email, format)
            id = self.spool.addSubscription(user)
            self.confirmSubscription(user, id)
            return 1
        
    def unsubscribe(
        self,
        email='',
        ):
        
        """ User unsubscription """ 
        if email not in self.users.keys():
            return 0
        else:
            user = self.users[email]
            id = self.spool.addUnsubscription(user)
            self.confirmUnsubscription(user, id)
            return 1

    def deluser(self, id):
	""" Delete a user by email """
        if self.users.has_key(id):
            del self.users[id]
            self._p_changed = 1

    def adduser(self, REQUEST):
	""" Add a user """
        user = User(REQUEST['firstName'], REQUEST['lastName'], REQUEST['email'], REQUEST['format'])
        self.users[REQUEST['email']] = user
        self._p_changed = 1

    def moduserformat(self, email, format):
	""" Modify the format for a user """
	if self.users.has_key(email) and format != self.users[email].format:
	    self.users[email].format = format
	    self._p_changed = 1
	
    def listusers(self):
	""" List users """
	result = []
	for user in self.users.values():
	    l = [user.name[0], user.name[1], user.email, user.format]
	    result.append(l)
	return result

#############################
## E-mail posting function ##
#############################

    def sendAll(self, publi, subject, message_txt, message_html):
        """ Send the newsletter to all subscribed members """
        self.mailer.sendAll(publi, self.users, self.addTitle(subject), message_txt, message_html)

    def sendValidate(self, subject, publication_url):
        """ Send email to reviewers when publication submited """
        roles = self.get_local_roles()
        to=[]
        for r in roles:
            if 'Owner' or 'Manager' or 'Reviewer' in r[1] :
                # Got error if user not defined on CMF acl_users (returns None object)
                try :
                    e = self.portal_membership.getMemberById(r[0]).getProperty('email')
                    to += [e]
                except: pass
        self.mailer.sendValidate(to, subject, publication_url)
              
##########################################
## E-mail (parsing + sending) functions ##
##########################################

    def parseMailSubject(self, mfrom, to, subject):
        """ Parse e-mail subject and eventually send to spool. """
        tokens = string.split(subject)
        ## case 1: mail to confirm unsubscription
        if self.UNSUB in tokens and 'id:' in tokens :
            email = self.spool.checkUnsubscription(subject)
            if email is not None:
                self.unsubscriptionDone(self.users[email])
        ## case 1b: mail to request an unsubscription
        elif self.UNSUB in tokens and 'mail:' in tokens :
            m = re.match(".*mail: ([^ ]*).*", subject)
            if m:
                email = m.group(1)
                self.unsubscribe(email)
            
        ## case 2: mail to confirm subscription 
        elif self.SUB in tokens and 'id:' in tokens :
            user = self.spool.checkSubscription(subject)
            if user is not None:
                self.subscriptionDone(user)
        ## case 3: mail format modification
        elif self.MOD in tokens and 'mail:' in tokens and 'format:' in tokens :
            m = re.match(".*mail: ([^ ]*).*format: ([0-9]).*", subject)
            if m:
                email = m.group(1)
                format = int(m.group(2))
		self.moduserformat(email, format)
		self.welcome(self.users[email])

    def confirmSubscription(self, user, id):
        """ Send e-mail to request user subscription confirmation """
        message = """
You have requested subscription to "%s".
Please confirm your subscription by replying to this mail (keep entire subject)

Thank you for your attention.
""" %self.title
        if hasattr(self, 'subscription_message'):
            message = self.subscription_message
        subject = self.formatConfirmSubject(self.SUB, user, id)
        self.mailer.mailSubscribe(user, subject, message)

    def confirmUnsubscription(self, user, id):
        """ Send e-mail to request user unsubscription confirmation """
        message = """
You have requested unsubscription from "%s".
Please confirm your unsubscription by replying to this mail (keep entire subject)

Thank you for your attention.
""" %self.title
        if hasattr(self, 'unsubscription_message'):
            message = self.unsubscription_message
        subject = self.formatConfirmSubject(self.UNSUB, user, id)
        self.mailer.mailUnsubscribe(user, subject, message)

    def welcome(self, user):
        """ send a welcome message to the newly subscribed user """
        if hasattr(self, 'welcome_release') and hasattr(self, self.welcome_release):
            release = self[self.welcome_release]
            [html, text] = release.getBodies()
            subject = self.addTitle(release.title_or_id())
            self.mailer.mailTo(user, subject, user.format and html or text)

    def subscriptionDone(self, user):
        """ Send e-mail to confirm user subscription """
        message = """
You have been added to "%s".

Thank you for your attention.
""" %self.title
        if hasattr(self, 'confirmation_message'):
            message = self.confirmation_message
        subject = self.formatDoneSubject(self.SUB, user)
        self.mailer.mailSubscribe(user, subject, message)
	self.users[user.email] = user
	self._p_changed = 1
        # Send the welcome release if set
        self.welcome(user)

    def unsubscriptionDone(self, user):
        """ Send e-mail to confirm user unsubscription """
        message = """
You have been removed from "%s".

Thank you for your attention.
""" %self.title
        if hasattr(self, 'rconfirmation_message'):
            message = self.rconfirmation_message
        subject = self.formatDoneSubject(self.UNSUB, user)
        self.mailer.mailUnsubscribe(user, subject, message)
	del self.users[user.email]
	self._p_changed = 1

    def formatConfirmSubject(self, type, user, id):
        """ Returns formated subject to confirm (un)subscription """
        return self.addTitle("""Confirm %s - user: %s - id: %s""" %(type, user.email, id))

    def formatDoneSubject(self, type, user):
        """ Returns formated subject when (un)subscription done """
        return self.addTitle("""%s Done - user: %s""" %(type, user.email))


######################
## Internal Methods ##
######################

    def addTitle(self, subject):
        """ add newsletter title to subject """
        return """[%s] %s""" %(self.title, subject)
        
    def getMailHost(self):
        """ returns mailhost instance """
        root = getToolByName(self, 'portal_url').getPortalObject()
        return getattr(root, 'MailHost') 

 
##########################
## Class Initialisation ##
##########################

InitializeClass(Newsletter)

