# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
A Publication is a Newsletter release. 

$Id: Publication.py,v 1.4 2003/08/01 15:20:11 terraces Exp $
"""

## Python imports
import whrandom
import re, string, locale
from cStringIO import StringIO

## Zope imports
from DateTime import DateTime
import Globals
from Globals import DTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base

## CMF imports
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDefault import Document
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent, ModifyPortalContent
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName

## Plone imports
from Products.CMFPlone.PloneFolder import *

# Here you could use a list of dictionaries or a dictionnary
# Take care of the fti argument in utils.ContentInit in __init__.py
# because if it is a list of lists, you will have a really bad surprise :
# everything would work perfectly, but you won't be able to add a factory
# based portal type anymore !
# Clearly : the fti must be a list of dictionnaries, not a list of lists
factory_type_information =   ({ 'id'             : 'Publication'
                             , 'meta_type'      : 'Publication'
                             , 'description'    : """\
Create a publication for the newsletter."""
                             , 'icon'           : 'publication_icon.png'
# This is the name of the product
# If you put something else, everything would work,
# but CMF members won't see the type in the NEW list.
                             , 'product'        : 'PloneNewsletter'
                             , 'factory'        : 'addPublication'
                             , 'immediate_view' : 'folder_contents'
                             , 'filter_content_types' : 1
                             , 'allowed_content_types' : ('Article',)
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'folder_contents'
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'webview'
                                  , 'name'          : 'Web view'
                                  , 'action'        : 'publi_webview'
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'mailview'
                                  , 'name'          : 'Mail view'
                                  , 'action'        : 'publi_mailview'
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'txtview'
                                  , 'name'          : 'Text view'
                                  , 'action'        : 'publi_txtview'
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'portal_form/folder_edit_form'
                                  , 'permissions'   : (ModifyPortalContent,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'customize'
                                  , 'name'          : 'Customize'
                                  , 'action'        : 'customize'
                                  , 'permissions'   : (ModifyPortalContent,)
                                  , 'category'      : 'object'
                                  }
                                , { 'id'            : 'status'
                                  , 'name'          : 'Status'
                                  , 'action'        : 'publi_status'
                                  , 'permissions'   : (View,)
                                  , 'category'      : 'object'
                                  }
                                )
                             }
                            )

# Inherits from PortalContent so it cat be workflowed and indexed
class Publication(PortalFolder, PortalContent, DefaultDublinCoreImpl,):
    """
        Contains words definitions
    """
    meta_type = 'Publication'
    portal_type = 'Publication'

    security = ClassSecurityInfo()

    def __init__( self, id, title='' ):
        self.id = id
        self.title = title
        self.description = ''

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        " Add self to the workflow and catalog. "
        # Recurse in the children (ObjectManager)
        PortalFolder.manage_afterAdd(self, item, container)
        # Add self to workflow and catalog
        PortalContent.manage_afterAdd(self, item, container)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        " Remove self from the workflow and catalog. "
        # We don't call PortalContent.manage_beforeDelete because
        #  it deals with talkbacks which are subobjects...
        # Remove self from catalog
        if aq_base(container) is not aq_base(self):
            self.unindexObject()
        # Then recurse in the children (ObjectManager)
        PortalFolder.manage_beforeDelete(self, item, container)

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ View all articles as html """
        return self.publi_webview(REQUEST, RESPONSE)

    # Public access is needed when called through XMLRPC from NLParser.py
    security.declarePublic('striptext')
    def striptext(self, s):
        """ Strip text from all html tags """
        s = string.replace(s, '<p>', ' @#BR@ ')
        s = string.replace(s, '<br>', ' @#BR@ ')
        parser = StrippingParser()
        parser.feed(s)
        parser.close()
        text = parser.result
        lines = []
        words = string.split(text)
	if not words:
	    return text
        current = words.pop(0)
        if current == '@#BR@':
            current = ''
        for word in words:
            increment = 1 + len(word)
            if word == '@#BR@':
                lines.append(current)
                current = ''
            elif len(current) + increment > 76:
                lines.append(current)
                current = word
            else:
                current = current + ' ' + word
        lines.append(current)
        text = string.join(lines, '\n')
        return text

    security.declareProtected(AddPortalFolders, 'ManageProperties')
    def customize(self, REQUEST, RESPONSE):
        """ This method creates an index_html document that the user
        will be able to edit for customization purposes"""
        self.genIndexes(REQUEST, RESPONSE, 1)
        REQUEST.set('portal_status_message', 'The HTML and TXT indexes have been generated. You can now customize them.')
        return self.folder_contents(REQUEST, RESPONSE)

    def genIndexes(self, REQUEST, RESPONSE, delete=0):
        """ Create indexes if needed """
        for id in ['index.html', 'index.txt']:
          if delete and hasattr(self.aq_explicit, id) :
            self.manage_delObjects(id)

        id = 'index.html'
        if not hasattr(self.aq_explicit, id):
            Document.addDocument(self, id, 'HTML Index', text_format='html', text=self.publi_htmlindex(REQUEST, RESPONSE))
            self[id]._setPortalTypeName('Document')
            self[id].reindexObject()

        id= 'index.txt'
        if not hasattr(self.aq_explicit, id):
            # We cut the enclosing <pre> tags
            text = self.publi_txtindex(REQUEST, RESPONSE)[5:-7]
            Document.addDocument(self, id, 'Text Index', text_format='text', text=text)
            self[id]._setPortalTypeName('Document')
            self[id].reindexObject()


    security.declarePublic('send')
    def send(self, context, all=1):
        """ Call the send method of the Newsletter,
            passing it text and html bodies """
        [htmlbody, txtbody] = self.getBodies()
        self.sendAll(self, self.title_or_id(), txtbody, htmlbody)

    security.declarePublic('validate')
    def validate(self, context, all=1):
        """ Send e-mail to admin, telling them the newsletter should be validated """
        [htmlbody, txtbody] = self.getBodies()
        self.sendValidate('[Publication submited for review] %s' %self.title_or_id(), self.absolute_url())

    security.declarePublic('getBodies')
    def getBodies(self):
        """Returns the Newsletter in html and text formats"""
        if hasattr(self, 'mailskin'):
            mailskin = self.mailskin
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal._v_skindata = (self.REQUEST, self.getSkinByName(mailskin), {})
        htmlbody = self.publi_mailview()
        txtbody = self.publi_txtindex()
        txtbody = string.replace(txtbody[5:-7], '&quot;', '"')
        txtbody = string.replace(txtbody, '&nbsp;', ' ')
        txtbody = string.replace(txtbody, '&amp;', '&')
        txtbody = string.replace(txtbody, '&eacute;', 'é')
        txtbody = string.replace(txtbody, '&egrave;', 'è')
        txtbody = string.replace(txtbody, '&#8217;', "'")
        txtbody = string.replace(txtbody, '&#8216;', "'")
        txtbody = string.replace(txtbody, '&#339;', 'oe')
        txtbody = string.replace(txtbody, '&#8230;', '...')
        txtbody = string.replace(txtbody, '&#8211;', '-')
        txtbody = string.replace(txtbody, '&#8222;', '"')
        txtbody = string.replace(txtbody, '&#8364;', 'EUR')
        return [htmlbody, txtbody]
        
    security.declareProtected(AddPortalFolders, 'addPublication')
    def addPublication(self, id, title='', REQUEST=None):
        """Add a new Publication object with id *id*.
        """
        ob=Publication(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            return self.folder_contents( # XXX: ick!
                self, REQUEST, portal_status_message="Publication added")

Globals.InitializeClass(Publication)

def addPublication(self, id, title='', REQUEST=None):
    """ Add a publication """
    o = Publication(id, title)
    self._setObject(id, o)

# HTML Stripper
import sgmllib, string

class StrippingParser(sgmllib.SGMLParser):
    
    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib
    
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def unknown_starttag(self, tag, attrs):
        pass

    def unknown_endtag(self, tag):
        pass

