# coding=utf-8
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider

class NavLinks(GroupContentProvider):
    def __init__(self, context, request, view):
        GroupContentProvider.__init__(self, context, request, view)
        self.__updated = False
        
    def update(self):
        self.__updated = True
        
    def render(self):
        if not self.__updated:
            raise UpdateNotCalled

        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(self)

