## Script (Python) "has_topics"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= topic
##title=Returns if newsletter publication has topics
##

for o in context.objectValues('Article'):
    if o.topic == topic:
        return 1
return 0 

