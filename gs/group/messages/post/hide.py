# coding=utf-8
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from interfaces import IHide

class HidePost(GroupForm):
    form_fields = form.Fields(IHide)
    label = _(u'Hide a Post')
    pageTemplateFileName = 'browser/templates/hide.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        GroupForm.__init__(self, context, request)

    @form.action(label=_('Hide'), failure='handle_failure')
    def handle_hide(self, action, data):
        self.status = u''
        uri = '/r/topic/%s' % data['postId']
        self.request.RESPONSE.redirect(uri)
    
    def handle_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

