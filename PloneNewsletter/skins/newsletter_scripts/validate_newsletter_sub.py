## Script (Python) "validate_newsletter_sub"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a newsletter subscribtion form
##

validator = context.portal_form.createForm()
validator.addField('firstName', 'String', required=0)
validator.addField('lastName', 'String', required=0)
validator.addField('email', 'String', required=1)

errors = validator.validate(context.REQUEST)

return errors
