## Script (Python) "newsletter_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= id='', description, topics, field_mailFrom, field_nameFrom, disclaimer,  signature, field_title='', errors
##title=Edit a newsletter

new_context = context.portal_factory.doCreate(context, id)
new_context.edit(field_title,
                description,
                topics,
                field_mailFrom,
                field_nameFrom,
                disclaimer,
                signature,
                )
new_context.plone_utils.contentEdit(context,
                            		id = id,
                                    title = field_title,
                                    description = description,
                                    topics = topics,
                                    mailFrom = field_mailFrom,
                                    nameFrom = field_nameFrom,
                                    disclaimer = disclaimer,
                                    signature = signature
                                    )

return ('success', 
    new_context, 
    {'portal_status_message':context.REQUEST.get('portal_status_message', 'Newsletter changes saved.')}
)
