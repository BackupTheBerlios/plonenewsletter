## Script (Python) "user_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##
from Products.CMFPlone import transaction_note

REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
    transaction_note( context.absolute_url() + ' ' + str(REQUEST['ids'])+' has been deleted' )
    for id in REQUEST['ids']:
        context.deluser(id)
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/users_view?portal_status_message=Deleted.')
else:
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/users_view?portal_status_message=Please+select+one+or+more+items+first.')
