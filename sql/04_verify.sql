-- Verification for Milestone 1 (run in the Supabase SQL Editor)

-- A) Row counts. Expected: staff 8, beans 12, shipments 15, orders 12, badge_logs 30
SELECT 'staff' AS t, COUNT(*) FROM staff
UNION ALL SELECT 'beans', COUNT(*) FROM beans
UNION ALL SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'badge_logs', COUNT(*) FROM badge_logs;

-- B) Permission summary. Expected:
--    runner_reads_beans = true,  runner_writes_orders = false, runner_uses_app = false,
--    runner_uses_auth = false,   app_inserts_audit = true,     app_updates_audit = false,
--    app_deletes_audit = false,  anon_reads_beans = false,     rls_on_beans = true
SELECT
  has_table_privilege('quiz_runner', 'public.beans', 'SELECT')        AS runner_reads_beans,
  has_table_privilege('quiz_runner', 'public.orders', 'DELETE')       AS runner_writes_orders,
  has_schema_privilege('quiz_runner', 'app', 'USAGE')                 AS runner_uses_app,
  has_schema_privilege('quiz_runner', 'auth', 'USAGE')                AS runner_uses_auth,
  has_table_privilege('quiz_app', 'app.query_audit', 'INSERT')        AS app_inserts_audit,
  has_table_privilege('quiz_app', 'app.query_audit', 'UPDATE')        AS app_updates_audit,
  has_table_privilege('quiz_app', 'app.query_audit', 'DELETE')        AS app_deletes_audit,
  has_table_privilege('anon', 'public.beans', 'SELECT')               AS anon_reads_beans,
  (SELECT relrowsecurity FROM pg_class WHERE oid = 'public.beans'::regclass) AS rls_on_beans;

-- C) Role settings. Expected quiz_runner row to include
--    default_transaction_read_only=on, statement_timeout=5s, search_path=public
SELECT r.rolname, s.setconfig
FROM pg_db_role_setting s JOIN pg_roles r ON r.oid = s.setrole
WHERE r.rolname IN ('quiz_runner', 'quiz_app');
