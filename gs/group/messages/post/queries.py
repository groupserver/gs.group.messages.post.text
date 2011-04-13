# coding=utf-8
import sqlalchemy as sa
from datetime import datetime
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

    def hide_post(self, postId, userId, reason):
        now = datetime.now(UTC)
        self.update_post_table(postId, now)
        self.update_hidden_post_table(postId, now, userId, reason)
        
    def update_post_table(self, postId, dt):
        u = self.postTable.update(self.postTable.c.post_id == postId)
        u.execute(hidden = dt)
    
    def update_hidden_post_table(self, postId, dt, userId, reason):
        i = self.hiddenPostTable.insert()
        i.execute(post_id = postId, 
            date_hidden = dt,
            hiding_user = userId,
            reason = reason)

