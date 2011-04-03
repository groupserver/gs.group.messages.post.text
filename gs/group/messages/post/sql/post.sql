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
    hidden            TIMESTAMP WITH TIME ZONE,
);
-- Existing installs will need to update the post table:
-- ALTER TABLE post 
--  ADD COLUMN hidden TIMESTAMP WITH TIME ZONE;
CREATE INDEX site_group_idx ON post USING BTREE (site_id, group_id);
CREATE INDEX topic_idx ON post USING BTREE (topic_id);

