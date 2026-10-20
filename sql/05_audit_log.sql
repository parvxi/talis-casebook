-- Audit log upgrade (extra credit). Run in the Supabase SQL Editor AFTER 02_roles.sql.
-- Safe to run more than once.

-- 1) Record who did what: the action (run/submit), which mission, and the signed-in email.
ALTER TABLE app.query_audit ADD COLUMN IF NOT EXISTS action      TEXT;
ALTER TABLE app.query_audit ADD COLUMN IF NOT EXISTS question_id INT;
ALTER TABLE app.query_audit ADD COLUMN IF NOT EXISTS user_email  TEXT;

-- 2) Integrity: the log is append-only.
--    Layer 1 (02_roles.sql): quiz_runner (the taker role) has no access to schema app at all,
--            and quiz_app has INSERT/SELECT only, no UPDATE or DELETE.
--    Layer 2 (here): a trigger rejects UPDATE, DELETE and TRUNCATE for every role,
--            including the table owner, so history cannot be rewritten by mistake either.
CREATE OR REPLACE FUNCTION app.reject_audit_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'app.query_audit is append-only (% blocked)', TG_OP;
END;
$$;

DROP TRIGGER IF EXISTS query_audit_append_only ON app.query_audit;
CREATE TRIGGER query_audit_append_only
  BEFORE UPDATE OR DELETE ON app.query_audit
  FOR EACH ROW EXECUTE FUNCTION app.reject_audit_change();

DROP TRIGGER IF EXISTS query_audit_no_truncate ON app.query_audit;
CREATE TRIGGER query_audit_no_truncate
  BEFORE TRUNCATE ON app.query_audit
  FOR EACH STATEMENT EXECUTE FUNCTION app.reject_audit_change();

-- Check (expected: 3 rows: action, question_id, user_email)
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'app' AND table_name = 'query_audit'
  AND column_name IN ('action', 'question_id', 'user_email');
