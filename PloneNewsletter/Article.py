# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
Article product for PloneNewsletter.

$Id: Article.py,v 1.1 2002/11/05 11:26:39 terraces Exp $
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

from Products.CMFDefault.Document import Document

from DateTime import DateTime

#
import re
import whrandom
from User import User
from Spool import Spool
from Mailer import Mailer
import string

####################################
## Article properties and methods ##
####################################

factory_type_information = (
    {'id'                   : 'Article',
    'meta_type'             : 'Article',
    'description'           : ('Newsletter article.'),
    'icon'                  : 'document_icon.png',
    'product'               : 'PloneNewsletter',
    'factory'               : 'addArticle',
    'immediate_view'        : 'document_view',
    'actions'       : (
        {'id'           : 'view',
         'name'         : 'View',
         'action'       : 'document_view',
         'permissions'  : (CMFCorePermissions.View,),
        },
        {'id'           : 'edit',
         'name'         : 'Edit',
         'action'       : 'portal_form/article_edit_form',
         'permissions'  : (CMFCorePermissions.ModifyPortalContent,),
        },
        {'id'           : 'metadata'
        , 'name'        : 'Metadata'
	    , 'action'      : 'metadata_edit_form'
	    , 'permissions' : (CMFCorePermissions.ManageProperties,)
        },
        ),
    }
)

def addArticle(self, 
        id,
        title='',
        position='',
        topic='',
        description='',
        text='',
        source='',
        url='',
        text_format='',
        ):
    """ add an article """
    article_object = Article(id, title, position, topic, description, source, url, text, text_format)
    self._setObject(id, article_object)

class Article(Document):
	
    """ Article Class """

    __implements__ = Document.__implements__

    meta_type = 'Article'
    portal_type = 'Article'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self,
                id, 
                title='',
                position='',
                topic='',
                description='',
                source='',
                url='',
                text='',
        		text_format='',
        ):
        """ Instanciates an Article """
        Document.__init__(self, id, title, description, text_format, text)
        self.position = position
        self.topic = topic
        self.source = source
        self.url = string.split(url,'\n')
		
    def edit(self,   
            title='',
            position='',
            topic='',
            description='',
            source='',
            url='',
            text='',
            text_format='',
            file='',
            ):
        """ Edit article properties """     
        Document.edit(self, text_format, text, file)
        self.editMetadata(title=title, description=description)
        self.position=position
        self.topic=topic
        self.source = source
        self.url = string.split(url,'\n')

InitializeClass(Article)

