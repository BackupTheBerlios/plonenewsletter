## Script (Python) "newsletter_unsub"
##parameters=field_email
##title=Remove user from newsletter

import string

REQUEST=context.REQUEST

errors=context.validate_newsletter_unsub()
if errors:
    send_form=getattr(context, context.getTypeInfo().getActionById('view'))
    return send_form(REQUEST)

# subscribe to the mailing-list
unsubscribed = context.unsubscribe(field_email)

# thanks page
REQUEST.set('title', 'Thank you')
REQUEST.set('portal_status_message', 'Done.')

# confirmation message
thanx=''
if unsubscribed: thanx='You will get a mail to confirm your unsubscription in a few minutes; thank you for your interest.'
else: thanx='You are not member of this newsletter.'

qst='portal_status_message=%s' % string.replace(thanx, ' ', '+')

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s?%s' % ( string.split(REQUEST.HTTP_REFERER, '?')[0]
                                                , qst
                                                ) )
