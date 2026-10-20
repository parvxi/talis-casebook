-- Roles and app schema for The Roastery Heist (run in the Supabase SQL Editor AFTER 01_schema_seed.sql)
-- Safe to run more than once.
--
-- PASSWORDS: this file keeps the placeholders CHANGE-ME-runner / CHANGE-ME-app on purpose.
-- Replace them ONLY in the Supabase SQL Editor, never in this file, and never commit real values.
-- Use letters and digits only (e.g. `openssl rand -hex 24`) so the connection string needs no escaping.

CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.quiz_submissions (
  id             BIGSERIAL PRIMARY KEY,
  user_id        UUID NOT NULL,                 -- Supabase auth user.id
  question_id    INT  NOT NULL,
  submitted_sql  TEXT NOT NULL,
  is_correct     BOOLEAN NOT NULL,
  points_awarded INT  NOT NULL,
  submitted_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS app.query_audit (            -- extra credit
  id            BIGSERIAL PRIMARY KEY,
  user_id       UUID,
  sql_text      TEXT NOT NULL,
  ok            BOOLEAN NOT NULL,
  error_text    TEXT,
  rows_returned INT,
  ran_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create the roles only if they do not exist yet (CREATE ROLE has no IF NOT EXISTS)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'quiz_runner') THEN
    CREATE ROLE quiz_runner LOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'quiz_app') THEN
    CREATE ROLE quiz_app LOGIN;
  END IF;
END
$$;

ALTER ROLE quiz_runner WITH LOGIN PASSWORD 'CHANGE-ME-runner';
ALTER ROLE quiz_app    WITH LOGIN PASSWORD 'CHANGE-ME-app';

-- 1) Student sandbox role: can only SELECT from the five quiz tables
GRANT USAGE ON SCHEMA public TO quiz_runner;
GRANT SELECT ON public.staff, public.beans, public.shipments, public.orders, public.badge_logs TO quiz_runner;
ALTER ROLE quiz_runner SET default_transaction_read_only = on;
ALTER ROLE quiz_runner SET statement_timeout = '5s';
ALTER ROLE quiz_runner SET search_path = public;

-- 2) Application role: writes answers and audit rows, nothing else
GRANT USAGE ON SCHEMA app TO quiz_app;
GRANT INSERT, SELECT ON app.quiz_submissions TO quiz_app;
GRANT INSERT, SELECT ON app.query_audit TO quiz_app;     -- no UPDATE/DELETE: nobody can rewrite history (SELECT is needed for RETURNING and the audit view)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO quiz_app;
ALTER ROLE quiz_app SET statement_timeout = '5s';
