SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE post (
    post_id           TEXT                     PRIMARY KEY,
    topic_id          TEXT                     NOT NULL,
    group_id          TEXT                     NOT NULL,
    site_id           TEXT                     NOT NULL,
    user_id           TEXT                     NOT NULL,
    in_reply_to       TEXT                     NOT NULL DEFAULT ''::TEXT,
    subject           TEXT                     NOT NULL DEFAULT ''::TEXT,
    date              TIMESTAMP WITH TIME ZONE NOT NULL,
    body              TEXT                     NOT NULL DEFAULT ''::TEXT,
    htmlbody          TEXT                     NOT NULL DEFAULT ''::TEXT,
    header            TEXT                     NOT NULL,
    has_attachments   BOOLEAN                  NOT NULL,
    hidden            TIMESTAMP WITH TIME ZONE
);
-- Installs prior to GS 11.04 will need to update the post table:
-- ALTER TABLE post 
--  ADD COLUMN hidden TIMESTAMP WITH TIME ZONE;
CREATE INDEX site_group_idx ON post USING BTREE (site_id, group_id);
CREATE INDEX topic_idx ON post USING BTREE (topic_id);

-- Create the row-count table, which is used all over the place
-- TODO: Move to a base product. Maybe create a gs.base or put it in
-- gs.group.messages.base?
CREATE TABLE rowcount (
    table_name  text NOT NULL,
    total_rows  bigint,
    PRIMARY KEY (table_name)
);

CREATE OR REPLACE FUNCTION count_rows()
RETURNS TRIGGER AS
'
   BEGIN
      IF TG_OP = ''INSERT'' THEN
         UPDATE rowcount
            SET total_rows = total_rows + 1
            WHERE table_name = TG_RELNAME;
      ELSIF TG_OP = ''DELETE'' THEN
         UPDATE rowcount
            SET total_rows = total_rows - 1
            WHERE table_name = TG_RELNAME;
      END IF;
      RETURN NULL;
   END;
' LANGUAGE plpgsql;

-- Initialise the trigger and rowcount for the post table
BEGIN;
   -- Make sure no rows can be added to post until we have finished
   LOCK TABLE post IN SHARE ROW EXCLUSIVE MODE;

   CREATE TRIGGER count_post_rows
      AFTER INSERT OR DELETE on post
      FOR EACH ROW EXECUTE PROCEDURE count_rows();
   
   -- Initialise the row count record
   DELETE FROM rowcount WHERE table_name = 'post';

   INSERT INTO rowcount (table_name, total_rows)
   VALUES  ('post',  (SELECT COUNT(*) FROM post));
COMMIT;

