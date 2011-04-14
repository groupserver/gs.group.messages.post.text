# coding=utf-8
from zope.component import createObject
from queries import PostQuery

class HiddenPostInfo(object):
    def __init__(self, context, postId):
        self.postId = postId
        
        da = context.zsqlalchemy
        q = PostQuery(context, da)
        
        hiddenPostDetails = q.get_hidden_post_details(postId)
        m = 'No details for the hidden post %s' % postId
        assert hiddenPostDetails, m

        self.adminInfo = createObject('groupserver.UserFromId',
                            context, hiddenPostDetails['hiding_user'])

        self.date = hiddenPostDetails['date_hidden']
        self.reason = hiddenPostDetails['reason']

