# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
PloneNewsletter initialization class

$Id: __init__.py,v 1.1 2002/11/05 11:26:40 terraces Exp $
"""

import Newsletter
import Publication
import Article

from Products.CMFCore import utils, CMFCorePermissions, DirectoryView

import sys
this_module = sys.modules[ __name__ ]

newsletter_globals = globals()

## declare class and constuctors 
## avoir si on doit integrer Users et les clsses non CMF ???
contentClasses = (Newsletter.Newsletter,
                    Publication.Publication,
                    Article.Article,
                    )
contentConstructors = (Newsletter.addNewsletter,
                        Publication.addPublication,
                        Article.addArticle,
                        )
contentFactoryTypeInformation = (Newsletter.factory_type_information,
                                Publication.factory_type_information,
                                Article.factory_type_information,
                                )
                                
## declare skins
DirectoryView.registerDirectory( 'skins', newsletter_globals )

z_bases = utils.initializeBasesPhase1(contentClasses, this_module)

## init
def initialize(context):
    utils.initializeBasesPhase2(z_bases, context)
    utils.ContentInit( 'CMF Newsletter'
               , content_types = contentClasses
               , permission = CMFCorePermissions.AddPortalContent
               , extra_constructors = contentConstructors
               , fti = contentFactoryTypeInformation
               ).initialize( context )


