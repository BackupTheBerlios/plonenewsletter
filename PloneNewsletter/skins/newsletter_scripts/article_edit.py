## Script (Python) "article_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= id='', title, position, topic, description, source, url, text, text_format, file, errors
##title=Edit an article

new_context = context.portal_factory.doCreate(context, id)
new_context.edit(title,
                position,
                topic,
                description,
                source,
                url,
                text,
                text_format,
                file,
                )
new_context.plone_utils.contentEdit(context,
                            		id = id,
                                    title = title,
                                    description = description,
                                    source = source,
                                    url = url,
                                    topic = topic,
                                    text = text,
                                    text_format = text_format,
                                    file = file,			
                                    )

return ('success', 
    new_context, 
    {'portal_status_message':context.REQUEST.get('portal_status_message', 'Article changes saved.')}
)
