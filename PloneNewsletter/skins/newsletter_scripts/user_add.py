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
if REQUEST.has_key('email') and REQUEST['email']:
    transaction_note( context.absolute_url() + ' ' + str(REQUEST['email'])+' has been added' )
    context.adduser(REQUEST)
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/users_view?portal_status_message=Added.')
else:
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/users_view?portal_status_message=Please+enter+an+email.')
