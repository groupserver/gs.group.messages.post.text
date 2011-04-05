# coding=utf-8
import re
from urlparse import urlparse
from urllib import quote
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.errormesg.baseerror import BaseErrorPage

class PostHidden(BaseErrorPage):
    index = ZopeTwoPageTemplateFile('browser/templates/posthidden.pt')
    def __init__(self, context, request):
        BaseErrorPage.__init__(self, context, request)
        self.requested = request.form.get('q', '')

    def quote(self, msg):
        assert msg
        retval = quote(msg)
        assert retval
        return retval

    def __call__(self, *args, **kw):
        contentType = 'text/html; charset=UTF-8'
        self.request.response.setHeader('Content-Type', contentType)
        self.request.response.setStatus(410, lock=True)
        return self.index(self, *args, **kw)

