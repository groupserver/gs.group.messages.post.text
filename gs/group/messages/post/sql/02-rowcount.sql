SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

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
