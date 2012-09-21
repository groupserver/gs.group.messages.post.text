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
    hidden            TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    fts_vectors       tsvector -- PostgreSQL dependency
);

-- Installs up to and including GS 12.05 will need to update the post 
-- table:
-- ALTER TABLE post ADD COLUMN fts_vectors tsvector;
-- UPDATE post SET fts_vectors = 
--   to_tsvector('english', coalesce(subject,'') || ' ' || coalesce(body, ''));

-- Installs prior to GS 11.04 will need to update the post table:
-- ALTER TABLE post 
--  ADD COLUMN hidden TIMESTAMP WITH TIME ZONE;

CREATE INDEX site_group_idx ON post USING BTREE (site_id, group_id);
CREATE INDEX topic_idx ON post USING BTREE (topic_id);
CREATE INDEX post_fts_vectors ON post USING gin(fts_vectors);

CREATE TRIGGER fts_vectors_update 
  BEFORE INSERT or UPDATE ON post 
  FOR EACH ROW EXECUTE PROCEDURE 
    tsvector_update_trigger(fts_vectors, 'pg_catalog.english', subject, body);
