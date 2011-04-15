# coding=utf-8
from zope.formlib import form
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from interfaces import IHide
from queries import PostQuery

class HidePost(GroupForm):
    form_fields = form.Fields(IHide)
    label = _(u'Hide a Post')
    pageTemplateFileName = 'browser/templates/hide.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        GroupForm.__init__(self, context, request)

    @form.action(label=_('Hide'), failure='handle_failure')
    def handle_hide(self, action, data):
        self.postQuery.hide_post(data['postId'], self.loggedInUser.id, 
                                    data['reason'])
        self.status = u'Hidden the post.'
        uri = '/r/topic/%s#post-%s' % (data['postId'], data['postId'])
        self.request.RESPONSE.redirect(uri)
    
    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = _(u'<p>There is an error:</p>')
        else:
            self.status = _(u'<p>There are errors:</p>')

    @Lazy
    def postQuery(self):
        assert self.context
        da = self.context.zsqlalchemy
        assert da
        retval = PostQuery(self.context, da)
        assert retval
        return retval

    @Lazy
    def loggedInUser(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        assert retval
        assert not(retval.anonymous), 'Anon trying to hide a post!'
        return retval

