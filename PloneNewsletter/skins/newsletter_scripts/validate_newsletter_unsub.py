## Script (Python) "validate_newsletter_unsub"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a newsletter unsubscribtion form
##

validator = context.portal_form.createForm()
validator.addField('email', required=1)

errors = validator.validate(context.REQUEST)

return errors
