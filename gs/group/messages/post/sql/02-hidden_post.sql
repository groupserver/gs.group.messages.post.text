SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE hidden_post (
  post_id       TEXT REFERENCES post ON UPDATE CASCADE,
  date_hidden   TIMESTAMP WITH TIME ZONE NOT NULL,
  hiding_user   TEXT NOT NULL,
  reason        TEXT
);
CREATE UNIQUE INDEX hidden_post_pkey
  ON hidden_post
  USING BTREE(post_id, date_hidden);


