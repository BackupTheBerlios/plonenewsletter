## Script (Python) "newsletter_sub"
##parameters=field_firstName, field_lastName, field_email, format
##title=Add/remove user to/from newsletter

import string

REQUEST=context.REQUEST

errors=context.validate_newsletter_sub()
if errors:
    send_form=getattr(context, context.getTypeInfo().getActionById('view'))
    return send_form(REQUEST)

# subscribe to the mailing-list
subscribed = context.subscribe(field_firstName, field_lastName, field_email, format)

# thanks page
REQUEST.set('title', 'Thank you')
REQUEST.set('portal_status_message', 'Done.')

# confirmation message
thanx=''
if subscribed: thanx='You will get an e-mail to confirm your subscription in a few minutes; thank you for your interest.'
else: thanx='You are already member of this newsletter.'

qst='portal_status_message=%s' % string.replace(thanx, ' ', '+')

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s?%s' % ( string.split(REQUEST.HTTP_REFERER, '?')[0]
                                                , qst
                                                ) )
