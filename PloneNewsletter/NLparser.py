#!/usr/bin/python2.2

# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

#$Id: NLparser.py,v 1.1 2002/11/05 11:26:40 terraces Exp $

import StringIO
import sys
import rfc822
import xmlrpclib

__doc__ = """
Parse e-mail to send subject to newsletter spool
Usage:
    in /etc/aliases:
        foo-subscribe: "| /path/toscript/NLparser.py ZopeServerURL/newsletterPath
        foo-unsubscribe: "| /path/toscript/NLparser.py ZopeServerURL/newsletterPath
""" 

if __name__ == "__main__":

    args = sys.argv[1:]

    if args:
        ## get newsletterURL
        newsletterURL = sys.argv[1]
       
        ## get the email passend through a | and check it subject 
        data = StringIO.StringIO(sys.stdin.read())
        message = rfc822.Message(data)
        mfrom  =message.get('from')
        to = message.get('to')
        subject = message.get('subject')
        
        ## get server connexion and throws email infos
        newsletter = xmlrpclib.Server(newsletterURL)
        newsletter.parseMailSubject(mfrom, to, subject)

    else:
        print __doc__

