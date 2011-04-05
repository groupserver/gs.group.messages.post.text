# coding=utf-8
import sqlalchemy as sa
import datetime
from pytz import UTC

class PostQuery(object):
    def __init__(self, context, da):
        self.context = context
        
        self.postTable = da.createTable('post')
        self.hiddenPostTable = da.createTable('hidden_post')
        
    def get_hidden_post_details(self, postId):
        s = self.hiddenPostTable.select()
        s.append_whereclause(self.hiddenPostTable.c.post_id == postId)
        
        retval = None
        r = s.execute()
        if r.rowcount == 1:
            row = r.fetchone()
            retval = {
                'post_id':      row['post_id'],
                'date_hidden':  row['date_hidden'],
                'hiding_user':  row['hiding_user'],
                'reason':       row['reason']}
        return retval

