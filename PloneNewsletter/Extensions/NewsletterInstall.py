# This file is a component of PloneNewsletter product
# Copyright (C) 2002, Makina Corpus, http://makinacorpus.org
# Maintained by Alexandre Passant <apa@makinacorpus.org>
# and Arnaud Bienvenu <abi@makinacorpus.org>
# Released under GPL version 2. or later 
# See LICENSE.txt file or http://www.gnu.org/copyleft/gpl.html

"""
Install script to setup Newsletter, Publication and Article in a Plone Site instance 

$Id: NewsletterInstall.py,v 1.3 2003/08/01 15:20:11 terraces Exp $
"""

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.PloneNewsletter import Newsletter, newsletter_globals, Publication, PublicationWF, Article

from cStringIO import StringIO
import string

def install(self):
	
    """ Register Newsletter with the necessary tools """

    out = StringIO()

    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')
    wf = getToolByName(self, 'portal_workflow')

    ## Setup the objects
    for t in [Newsletter.factory_type_information, Publication.factory_type_information, Article.factory_type_information]:
        
        id = t['id']
        if id not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(id, cfm)
            out.write('Object "%s" registered in the types tool\n' %id)
        else:
            out.write('Object "%s" already registered in the types tool\n' %id)

        ## Setup the skin directory
        type = t['meta_type']
        if 'newsletter_scripts' not in skinstool.objectIds():
            addDirectoryViews(skinstool, 'skins', newsletter_globals)
            out.write('Added "%s" directory view to portal_skins\n' %type)
        else:
            out.write('Directory view "%s" already added to portal_skins\n' %type)

    for skindir in ['newsletter_scripts', 'plone_newsletter']:
        ## Setup the skins
        skins = skinstool.getSkinSelections()
        for skin in skins:
            path = skinstool.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            if skindir not in path:
                try: 
                    path.insert(path.index('plone_zest'), skindir)
                except ValueError:
                    path.append(skindir)
                path = string.join(path, ', ')
                skinstool.addSkinSelection(skin, path)
                out.write('Added "%s" to "%s" skin\n' %(skindir, skin))
            else:
              out.write('Skipping "%s" skin, "%s" is already set up\n' %(skin, skindir))
 
    ## Adds portal tabs in Publication and Newsletter view
    newftabs = ('Newsletter', 'Publication')
    ftabs = self.getProperty('use_folder_tabs')
    if ftabs : 
        ftabs += newftabs
        self._delPropValue('use_folder_tabs')
    else:
        ftabs = newftabs
    self._setProperty('use_folder_tabs',ftabs,'lines')
 
    ## Adds specific portal_navigation and portal_forms
    nav_tool = self.portal_navigation
    nav_tool.addTransitionFor('default','newsletter_edit','success','action:view')		
    nav_tool.addTransitionFor('default','newsletter_edit','failure','action:edit')		
    nav_tool.addTransitionFor('default','newsletter_edit_form','success','script:newsletter_edit')		
    nav_tool.addTransitionFor('default','newsletter_edit_form','failure','newsletter_edit_form')		
    nav_tool.addTransitionFor('default','article_edit','success','action:view')		
    nav_tool.addTransitionFor('default','article_edit','failure','action:edit')		
    nav_tool.addTransitionFor('default','article_edit_form','success','script:article_edit')		
    nav_tool.addTransitionFor('default','article_edit_form','failure','article_edit_form')		

    form_tool = self.portal_form
    form_tool.setValidators('newsletter_edit_form', ['validate_newsletter_edit'])
    form_tool.setValidators('article_edit_form', ['validate_article_edit'])

 
    ## Adds specific workflow to Publication, with script to send email
    wf.manage_addWorkflow(id='publi_wf', workflow_type='publi_wf (CMF default workflow [Revision 2])')
    wf.manage_changeWorkflows(default_chain='plone_workflow', props={'chain_Publication':'publi_wf'})
    ## add script
    scripts = getattr(wf.getWorkflowById('publi_wf'), 'scripts')
    ## send newsletter
    scripts.manage_addProduct['PythonScripts'].manage_addPythonScript('send')
    send = getattr(scripts, 'send')
    _send = """context.REQUEST.PARENTS[0].send(context)"""
    
    send.ZPythonScript_edit('attr', _send)
    ## submit newsletter for validation
    scripts.manage_addProduct['PythonScripts'].manage_addPythonScript('valid')
    valid = getattr(scripts, 'valid')
    valid.ZPythonScript_edit('attr', 'context.REQUEST.PARENTS[0].validate(context)')

    ## Ends
    return out.getvalue()

