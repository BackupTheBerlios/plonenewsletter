# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
Basic User class for Newsletter system.

$Id: User.py,v 1.1 2002/11/05 11:26:40 terraces Exp $
"""

from Globals import Persistent, InitializeClass
from AccessControl import ClassSecurityInfo

import string

class User(Persistent):
   
    ## email format
    # HTML = 1
    # Plain text = O
    ## 
    
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess("allow")

    def __init__(self, 
        firstName='',
        lastName='',
        email='',
        format='',
    ):			
        """ Initialize an instance of the class """
	
        ## set infos
        self.name = [string.strip(firstName), string.strip(lastName)]        
        self.email = email
        self.format = format
        
    def getTo(self):
        """ Returns a clean 'to' email header """
        if self.name!=['',''] :
            return '''"%s %s" <%s>''' %(self.name[0], self.name[1], self.email)
        else :
            return """<%s>""" %self.email

    def getName(self):
        """ Returns the name of the subscriber, if available """
        return string.join(self.name)

    def getFormat(self):
        """ Returns format value to 'Content-type' header """
        return self.format and 'html' or 'plain'
            
    def __str__(self):
        """ __str__ """
        return self.getTo()

##########################
## Class Initialisation ##
##########################

InitializeClass(User)

